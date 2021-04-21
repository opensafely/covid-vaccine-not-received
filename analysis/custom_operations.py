import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

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

backend, fig = practice_variation()
  
fig.savefig(f"output/{backend}/declines_by_practice_hist.png")



