''' This module generates charts from cohort.pickle rather than from the cumulative csvs.
''' 

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

wave_column_headings = {
    "total": "All",
    "all_priority": "Priority groups",
    "1": "In care home",
    "2": "80+",
    "3": "70-79",
    "4": "CEV",
    "5": "65-69",
    "6": "At risk",
    "7": "60-64",
    "8": "55-59",
    "9": "50-54",
    "0": "Other",
}

group_names = {
    "vacc_group":"Vaccinated", 
    "decline_group":"Declined", 
    "decline_total_group":"Declined - all",
    "other_reason_group":"Other reason",
    "declined_accepted_group": "Declined then accepted",
    "patient_id":"total"
    }

def compute_uptake_percent(uptake):#, labels):
    uptake_pc = 100 * uptake / uptake.loc["total"]
    uptake_pc.drop("total", inplace=True)
    uptake_pc.fillna(0, inplace=True)
    if set(uptake_pc.columns) == {"True", "False"}:
        # This ensures that chart series are always same colour.
        uptake_pc = uptake_pc[["True", "False"]]
    else:
        # Sort DataFrame columns so that legend is in the same order as chart series.
        uptake_pc.sort_values(
            uptake_pc.last_valid_index(), axis=1, ascending=False, inplace=True
        )
    #uptake_pc.rename(columns=labels, inplace=True)
    return uptake_pc


def practice_variation(input_path="output/cohort.pickle", output_dir="output"):
    ''' Calculates total patients per practice and of whom how many have had a vaccine to date, or declined
    Note: those declining only include those who have not later received a vaccine.
    '''
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")

    base_path = f"{output_dir}/{backend}/coverage_to_date"
    cohort = pd.read_pickle(input_path)

    practice_figures = cohort[["practice", "vacc_group", "decline_group", "patient_id"]]\
                        .groupby("practice").agg({"vacc_group":"sum", 
                                                  "decline_group":"sum", 
                                                  "patient_id":"nunique"})
    practice_figures = practice_figures.rename(columns={"patient_id":"patient_count"})
    
    # remove tiny practices and ensure that at least one patient has been vaccinated in each practice
    if backend=="expectations":
        practice_figures = practice_figures.loc[(practice_figures["patient_count"]>10)&(practice_figures["vacc_group"]>0)]
        
    else:
        practice_figures = practice_figures.loc[(practice_figures["patient_count"]>200)&(practice_figures["vacc_group"]>0)]
    
    # summarise data
    practice_count = len(practice_figures.index)
    counts = practice_figures.loc[practice_figures["decline_group"]>0]["decline_group"].count()
    d = {"practices with declines":counts, "total practices":practice_count}
    out = pd.Series(d, index=["practices with declines", "total practices"])
    out.to_csv(f"{output_dir}/{backend}/tables/practice_decline_summary.csv")

    practice_figures = practice_figures.assign(
        decline_per_1000 = 1000*practice_figures["decline_group"]/practice_figures["patient_count"],
        decline_per_1000_vacc = 1000*practice_figures["decline_group"]/practice_figures["vacc_group"],
        vacc_per_1000 = 1000*practice_figures["vacc_group"]/practice_figures["patient_count"]
    )

    for plot_type in ["hist","scatter"]:
        if plot_type=="hist":
            out = practice_figures.copy()
            fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
            bins = {0: [0,5,10,15,20,25,30,35,40,45,50,100,500],
                    1: [0,10,20,30,40,50,60,70,80,90,100,200,300,1000]}
            labels = {}

            for n, x in enumerate(["decline_per_1000", "decline_per_1000_vacc"]):
                labels[n] = [str(a)+"-<"+str(b) for (a,b) in zip(bins[n][:-1], bins[n][1:])]
                binned = pd.cut(out[x], bins=bins[n], labels=labels[n], retbins=False, include_lowest=True, right=False)
                binned = pd.DataFrame(binned.value_counts(normalize=True)).sort_index()

                axs[n].bar(binned.index, binned[x])
                axs[n].set_xlabel("Rate per 1000")
                axs[n].yaxis.set_major_formatter(PercentFormatter(1))
                axs[0].set_ylabel("Percent of practices")
                for tick in axs[n].get_xticklabels():
                    tick.set_rotation(90)

                title = "COVID Vaccines "+ x.replace("_"," ").replace("decline", "declined\n").replace("vacc","vaccinated").title()+" Patients"
                axs[n].set_title(title)

        if plot_type=="scatter":
            out = practice_figures.copy()
            # ensure that at least 1% of people in each practice have been vaccinated
            # (those with a v young population e.g. military may have small numbers)
            out = out.loc[out["vacc_per_1000"]>10]
            
            # group very large practices together to avoid identifiability
            out1 = out.loc[out["patient_count"]>=25_000]
            out1["patient_count"]= np.where(out1["patient_count"]>35_000, 35_000, 30_000)
            out2 = out.loc[out["patient_count"]<25_000]
            
            fig, axs = plt.subplots(2, 1, sharex=True, tight_layout=True, figsize=(6,8))
            for n, x in enumerate(["decline_group", "decline_per_1000_vacc"]):
                axs[n].scatter(out1["patient_count"]/1000, out1[x], alpha=0.5, marker='s', color='b')
                axs[n].scatter(out2["patient_count"]/1000, out2[x], alpha=0.5, marker='o', color='b')
                if "per_1000_vacc" in x:
                    title = "COVID Vaccines Declined\n per 1000 vaccinated patients per practice"
                    ylabel = "Rate per 1000"
                else:
                    title = "COVID Vaccines Declined\n per practice"
                    ylabel = "Vaccines Declined"
                axs[n].set_ylabel(ylabel)
                axs[n].set_title(title)
            axs[1].set_xlabel("Practice population (thousands)")
            

        fig.savefig(f"output/{backend}/charts/declines_by_practice_{plot_type}.png")



def declined_vaccinated(input_path="output/cohort.pickle", output_dir="output", wave_column_headings=wave_column_headings):
    ''' Counts patients who went from "Declined" to "Vaccinated".
        Creates a chart. 
    '''
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    base_path = f"{output_dir}/{backend}/coverage_to_date"
    cohort = pd.read_pickle(input_path)

    cohort["wave"] = cohort["wave"].astype(str)
    cohort = cohort[["wave", "vacc_group", "declined_accepted_group", "decline_total_group", "patient_id"]]\
                        .groupby("wave").agg({"vacc_group":"sum", 
                                              "declined_accepted_group":"sum", 
                                              "decline_total_group":"sum", 
                                              "patient_id":"nunique"})
    cohort = cohort.rename(columns=group_names, index=wave_column_headings)

    cohort = cohort.assign(
        per_1000 = 1000*cohort["Declined then accepted"]/cohort["total"],
        per_1000_vacc = 1000*cohort["Declined then accepted"]/cohort["Vaccinated"],
        converted = 1000*cohort["Declined then accepted"]/cohort["Declined - all"]
    )
    
    fig, axs = plt.subplots(3, 1, sharex=True, tight_layout=True, figsize=(6,12))
    for n, x in enumerate(["per_1000", "per_1000_vacc", "converted"]):
        cohort[x].plot(kind='bar', stacked=True, ax=axs[n])
        if x=="per_1000_vacc":
            title = "Patients Declining and later Accepting COVID Vaccines\n per 1000 vaccinated patients"  
        elif x=="converted":
            title = "Patients Declining and later Accepting COVID Vaccines\n per 1000 patients who declined"
        else:
            title = "Patients Declining and later Accepting COVID Vaccines\n per 1000 patients"
        
        axs[n].set_ylabel("Rate per 1000")
        axs[n].set_title(title)

    axs[1].set_xlabel("Priority group")

    fig.savefig(f"output/{backend}/charts/all_declined_then_accepted_by_wave.png")



def invert_df(df, group="all"):
    ''' "Inverts" df: 
    calculates the difference between the total population ("total" row) and 
    each other row in turn, so if df counts "patients vaccinated", the resulting
    df counts "patients NOT vaccinated".
    '''
    for i in df.index.drop("total"):
        df.loc[i] = df.loc["total"] - df.loc[i]

    return df
