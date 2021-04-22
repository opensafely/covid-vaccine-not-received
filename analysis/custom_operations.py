import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

group_names = {
    "vacc_group":"Vaccinated", 
    "decline_group":"Declined", 
    "vacc_not_successful_group":"Reached",
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

    fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

    for n, x in enumerate(["decline_per_1000", "decline_per_1000_vacc"]):
        # set weights to show percent rather than count of practices
        weights=np.ones(len(out)) / len(out)
        axs[n].hist(out[x], bins=15, weights=weights)
        title = "COVID Vaccines "+ x.replace("_"," ").replace("decline", "declined\n").replace("vacc","vaccinated").title()+" Patients"
        axs[n].set_title(title)
        axs[n].set_xlabel("Rate per 1000")
        axs[n].yaxis.set_major_formatter(PercentFormatter(1))

    axs[0].set_ylabel("Percent of practices")

    return (backend, fig)


def current_variation(input_path="output/cohort.pickle", output_dir="output"):
    ''' Groups patients into Vaccinated, Declined, Reached, Unvaccinated.
    '''
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    base_path = f"{output_dir}/{backend}/coverage_to_date"
    cohort = pd.read_pickle(input_path)

    current_figures = cohort[["wave", "vacc_group", "decline_group", "vacc_not_successful_group", "patient_id"]]\
                        .groupby("wave").agg({"vacc_group":"sum", 
                                              "decline_group":"sum", 
                                              "vacc_not_successful_group":"sum",
                                              "patient_id":"nunique"})
    current_figures = current_figures.rename(columns=group_names)

    current_figures = current_figures.assign(
        Unvaccinated = current_figures["total"] - current_figures["Vaccinated"]
                                              - current_figures["Declined"]
                                              - current_figures["Reached"]
        )
    

    return current_figures


out = current_variation().transpose()
out = compute_uptake_percent(out).transpose().sort_index()

out.plot(kind='bar',stacked=True,)
#plt.legend(bbox_to_anchor=(1.05, 1),)
plt.show()



def invert_df(df, group="all"):
    ''' Inverts df
    '''

    for i in df.index.drop("total"):
        df.loc[i] = df.loc["total"] - df.loc[i]
    
    #out_path = "output/{backend}/cumulative_coverage/{group}/unreached/{group}_unreached_by_group.csv"
    #os.makedirs(out_path, exist_ok=True)

    return df

#out = invert()
#print(out)