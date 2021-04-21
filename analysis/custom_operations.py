import os
import pandas as pd

def practice_variation(input_path="output/cohort.pickle", output_dir="output"):
    ''' Calculates total patients per practice and of whom how many have had a vaccine to date, or declined
    '''
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    base_path = f"{output_dir}/{backend}/coverage_to_date"
    cohort = pd.read_pickle(input_path)

    practice_figures = cohort[["practice", "vacc_group", "decline_group", "patient_id"]].groupby("practice").count()
    practice_figures = practice_figures.rename(columns={"patient_id":"patient_count"})
    
    # remove tiny practices
    if backend=="expectations":
        practice_figures = practice_figures.loc[practice_figures["patient_count"]>5]
    else:
        practice_figures = practice_figures.loc[practice_figures["patient_count"]>100]
    
    practice_figures = practice_figures.assign(
        decline_per_1000 = 1000*practice_figures["decline_group"]/practice_figures["patient_count"],
        decline_per_1000_vacc = 1000*practice_figures["decline_group"]/practice_figures["vacc_group"]
    )

    return practice_figures

out = practice_variation()
print(out.head(20))

