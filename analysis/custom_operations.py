''' This module generates charts from cohort.pickle rather than from the cumulative csvs.
''' 

import os
import pandas as pd
import matplotlib.pyplot as plt
from plot_practice_charts import *
from ethnicities import high_level_ethnicities

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
    "declined_accepted_group": "Declined then received",
    "patient_id":"total"
    }

backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
out_path = f"output/{backend}/additional_figures"
os.makedirs(out_path, exist_ok=True)

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


def practice_variation(input_path="output/cohort.pickle", output_dir=out_path):
    ''' Calculates total patients per practice and of whom how many have had a vaccine to date, or declined
    Note: those declining only include those who have not later received a vaccine.
    '''
    cohort = pd.read_pickle(input_path)

    # limit to priority groups (ages 50+ and clinical priority groups)
    cohort = cohort.loc[cohort["wave"]!=0]

    practice_figures = cohort[["practice", "vacc_group", "decline_group", "patient_id"]]\
                        .groupby("practice").agg({"vacc_group":"sum", 
                                                  "decline_group":"sum", 
                                                  "patient_id":"nunique"})
    practice_figures = practice_figures.rename(columns={"patient_id":"patient_count"})
    
    # remove tiny practices by setting a minimum no of people in the priority groups
    #  and ensure that at least 10 patients have been vaccinated in each practice
    if backend=="expectations":
        practice_figures = practice_figures.loc[(practice_figures["patient_count"]>10)&(practice_figures["vacc_group"]>0)]
        
    else:
        practice_figures = practice_figures.loc[(practice_figures["patient_count"]>250)&(practice_figures["vacc_group"]>10)]
    
    # summarise data
    practice_count = len(practice_figures.index)
    counts = practice_figures.loc[practice_figures["decline_group"]>0]["decline_group"].count()
    d = {"practices with declines":counts, "total practices":practice_count}
    out = pd.Series(d, index=["practices with declines", "total practices"])
    out.to_csv(f"{output_dir}/practice_decline_summary.csv")

    practice_figures = practice_figures.assign(
        decline_per_1000 = 1000*practice_figures["decline_group"]/practice_figures["patient_count"],
        decline_per_1000_vacc = 1000*practice_figures["decline_group"]/practice_figures["vacc_group"],
        vacc_per_1000 = 1000*practice_figures["vacc_group"]/practice_figures["patient_count"]
    )

    plot_hist(df=practice_figures, output_dir=output_dir)
    plot_boxplot(df=practice_figures, backend=backend, output_dir=output_dir)
    plot_heatmap(df=practice_figures, backend=backend, output_dir=output_dir)




def declined_vaccinated(input_path="output/cohort.pickle", output_dir=out_path):
    ''' Counts patients who went from "Declined" to "Vaccinated".
        Creates a chart. 
    '''

    cohort = pd.read_pickle(input_path)

    cohort["wave"] = cohort["wave"].astype(str)
    cohort = cohort[["wave", "vacc_group", "declined_accepted_group", "decline_total_group", "patient_id"]]\
                        .groupby("wave").agg({"vacc_group":"sum", 
                                              "declined_accepted_group":"sum", 
                                              "decline_total_group":"sum", 
                                              "patient_id":"nunique"})
    cohort = cohort.rename(columns=group_names, index=wave_column_headings)

    cohort = cohort.assign(
        per_1000 = 1000*cohort["Declined then received"]/cohort["total"],
        per_1000_vacc = 1000*cohort["Declined then received"]/cohort["Vaccinated"],
        converted = 1000*cohort["Declined then received"]/cohort["Declined - all"]
    )
    
    fig, axs = plt.subplots(3, 1, sharex=True, tight_layout=True, figsize=(6,12))
    for n, x in enumerate(["per_1000", "per_1000_vacc", "converted"]):
        cohort[x].plot(kind='bar', stacked=True, ax=axs[n])
        if x=="per_1000_vacc":
            title = "Patients Declining and later Receiving COVID Vaccines\n per 1000 vaccinated patients"  
        elif x=="converted":
            title = "Patients Declining and later Receiving COVID Vaccines\n per 1000 patients who declined"
        else:
            title = "Patients Declining and later Receiving COVID Vaccines\n per 1000 patients"
        
        axs[n].set_ylabel("Rate per 1000")
        axs[n].set_title(title)

    axs[1].set_xlabel("Priority group")

    fig.savefig(f"{output_dir}/all_declined_then_accepted_by_wave.png")



def decl_acc_time_delay(input_path="output/cohort.pickle", output_dir=out_path):
    '''
    Measures the time between recorded decline and vaccination for each pt in the declined-then-accepted group,
    and groups to number of weeks.
    '''

    cohort = pd.read_pickle(input_path)

    # limit to priority groups (ages 50+ and clinical priority groups)
    cohort = cohort.loc[cohort["wave"]!=0]

    # filter to the declined-then-accepted group
    cohort = cohort.loc[cohort["declined_accepted_group"]==1]
    cohort = cohort[["wave", "declined_accepted_group", "patient_id", "vacc1_dat", "decl_first_dat", "high_level_ethnicity"]]
    cohort["wave"] = cohort["wave"].astype(str)
    # calculate no of days between recorded decline and vaccination.
    cohort["date_diff"] = cohort["vacc1_dat"] - cohort['decl_first_dat']
    
    # bin the data
    bins = [
        pd.Timedelta(days = 0),
        pd.Timedelta(days = 14),
        pd.Timedelta(days = 28),
        pd.Timedelta(weeks = 8),
        pd.Timedelta(weeks = 120)
        ]
    labels = ["0-<2 weeks", "2-<4 weeks", "1-<2 months", ">=2 months"]

    cohort["weeks_diff"] = pd.cut(cohort["date_diff"], bins=bins, labels=labels, retbins=False, include_lowest=True, right=False)
    

    # summarise for each group
    cohort_a = cohort.groupby(["wave","weeks_diff"])["patient_id"].count()
    cohort_a = cohort_a.rename(index=wave_column_headings)
    
    # low number suppression and rounding
    cohort_a = cohort_a.replace([1,2,3,4,5,6], 0)
    cohort_a = ((cohort_a // 7) * 7).astype(int)

    cohort_a.to_csv(f"{output_dir}/declined_accepted_weeks_by_wave.csv")

    
    # look at priority groups split by demographics

    cohort_b = cohort.copy()

    # group by wave and ethnicity
    cohort_b = cohort_b.groupby(["wave", "high_level_ethnicity","weeks_diff"])["patient_id"].count()
 
    # rename column headers and indices (2 levels)
    cohort_b = cohort_b.rename(index=high_level_ethnicities)
    cohort_b = cohort_b.rename(index=wave_column_headings)

    # low number suppression and rounding
    cohort_b = cohort_b.replace([1,2,3,4,5,6], 0)
    cohort_b = ((cohort_b // 7) * 7).astype(int)

    cohort_b.to_csv(f"{output_dir}/declined_accepted_weeks_by_wave_and_ethnicity.csv")
    

def invert_df(df, group="all"):
    ''' "Inverts" df: 
    calculates the difference between the total population ("total" row) and 
    each other row in turn, so if `df` counts "patients vaccinated", the resulting
    df counts "patients NOT vaccinated".
    '''
    for i in df.index.drop("total"):
        df.loc[i] = df.loc["total"] - df.loc[i]

    return df
