''' This module generates charts from cohort.pickle rather than from the cumulative csvs.
''' 

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

group_names = {
    "vacc_group":"Vaccinated", 
    "decline_group":"Declined", 
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
        practice_figures = practice_figures.loc[(practice_figures["patient_count"]>100)&(practice_figures["vacc_group"]>0)]
    
    practice_figures = practice_figures.assign(
        decline_per_1000 = 1000*practice_figures["decline_group"]/practice_figures["patient_count"],
        decline_per_1000_vacc = 1000*practice_figures["decline_group"]/practice_figures["vacc_group"]
    )

    out = practice_figures

    for plot_type in ["hist","scatter"]:
        if plot_type=="hist":
            fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

            for n, x in enumerate(["decline_per_1000", "decline_per_1000_vacc"]):
                # set weights to show percent rather than count of practices
                weights=np.ones(len(out)) / len(out)
                axs[n].hist(out[x], bins=15, weights=weights)
                axs[n].set_xlabel("Rate per 1000")
                axs[n].yaxis.set_major_formatter(PercentFormatter(1))
                axs[0].set_ylabel("Percent of practices")

                title = "COVID Vaccines "+ x.replace("_"," ").replace("decline", "declined\n").replace("vacc","vaccinated").title()+" Patients"
                axs[n].set_title(title)

        if plot_type=="scatter":
            fig, axs = plt.subplots(2, 1, sharex=True, tight_layout=True, figsize=(6,8))
            for n, x in enumerate(["decline_group", "decline_per_1000_vacc"]):
                axs[n].scatter(out["patient_count"]/1000, out[x])
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


# the following function could be carried out within generate_paper_outputs.py
def current_variation(input_path="output/cohort.pickle", output_dir="output"):
    ''' Groups patients into Vaccinated, Declined, Other reason, Unvaccinated.
        Presents the total number in each group for each wave/cohort.
    '''
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    base_path = f"{output_dir}/{backend}/coverage_to_date"
    cohort = pd.read_pickle(input_path)

    current_figures = cohort[["wave", "vacc_group", "decline_group", "other_reason_group", "patient_id"]]\
                        .groupby("wave").agg({"vacc_group":"sum", 
                                              "decline_group":"sum", 
                                              "other_reason_group":"sum",
                                              "patient_id":"nunique"})
    current_figures = current_figures.rename(columns=group_names)

    current_figures = current_figures.assign(
        Unvaccinated = current_figures["total"] - current_figures["Vaccinated"]
                                              - current_figures["Declined"]
                                              - current_figures["Other reason"]
        )
    
    current_figures = current_figures.transpose()
    out = compute_uptake_percent(current_figures).transpose().sort_index()
    
    fig, ax = plt.subplots()
    out.plot(kind='bar', stacked=True, ax=ax)
    ax.set_ylabel("Percent")
    plt.legend(loc="lower right")
    fig.savefig(f"output/{backend}/charts/declines_by_wave.png")

    return current_figures


# out = current_variation().transpose()
# out = compute_uptake_percent(out).transpose().sort_index()

# out.plot(kind='bar',stacked=True,)
# #plt.legend(bbox_to_anchor=(1.05, 1),)
# plt.show()

def declined_vaccinated(input_path="output/cohort.pickle", output_dir="output"):
    ''' Counts patients who went from "Declined" to "Vaccinated".
        Creates a chart. 
    '''
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    base_path = f"{output_dir}/{backend}/coverage_to_date"
    cohort = pd.read_pickle(input_path)

    cohort = cohort[["wave", "vacc_group", "declined_accepted_group", "patient_id"]]\
                        .groupby("wave").agg({"vacc_group":"sum", 
                                              "declined_accepted_group":"sum", 
                                              "patient_id":"nunique"})
    cohort = cohort.rename(columns=group_names)

    cohort = cohort.assign(
        per_1000 = 1000*cohort["Declined then accepted"]/cohort["total"],
        per_1000_vacc = 1000*cohort["Declined then accepted"]/cohort["Vaccinated"]
    )
    
    fig, axs = plt.subplots(2, 1, sharex=True, tight_layout=True, figsize=(6,8))
    for n, x in enumerate(["per_1000", "per_1000_vacc"]):
        cohort[x].plot(kind='bar', stacked=True, ax=axs[n])
        if x=="per_1000_vacc":
            title = "Patients Declining and later Accepting COVID Vaccines\n per 1000 vaccinated patients"  
        else:
            title = "Patients Declining and later Accepting COVID Vaccines\n per 1000 patients"
        
        axs[n].set_ylabel("Rate per 1000")
        axs[n].set_title(title)

    axs[1].set_xlabel("Cohort")

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
