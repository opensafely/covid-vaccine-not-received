import os
import pandas as pd

from compute_uptake import compute_uptake
from groups import at_risk_groups
from custom_operations import invert_df


demographic_cols = [
    "age_band",
    "sex",
    #"ethnicity",
    "high_level_ethnicity",
    "imd_band",
]
#at_risk_cols = ["atrisk_group"] #+ list(at_risk_groups)
other_cols = ["preg_group", "sevment_group", learndis_group]

cols = demographic_cols  + other_cols #+ at_risk_cols


def run(input_path="output/cohort.pickle", output_dir="output"):
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    base_path = f"{output_dir}/{backend}/cumulative_coverage"
    cohort = pd.read_pickle(input_path)

    for event_col, key in [
        ("vacc1_dat", "dose_1"),
        ("vacc_any_record_dat", "any_vaccine_record"),
        ("decl_dat", "declined"),
        #("cov2not_dat", "vaccine_not_done"),
	    #("cov1decl_acc_dat", "declined_accepted"),
    ]:

        # Compute uptake by wave
        dir_path = f"{base_path}/all/{key}"
        os.makedirs(dir_path, exist_ok=True)
        uptake = compute_uptake(cohort, event_col, "wave")
        uptake.to_csv(f"{dir_path}/all_{key}_by_group.csv")

        # Compute uptake by broader waves (1-3)
        uptake_w2 = compute_uptake(cohort, event_col, "wave2")
        uptake_w2.to_csv(f"{dir_path}/all_{key}_by_group2.csv")

        # for "any vaccine record" calculate the inverse ie. no of patients with NO vaccine related record
        if event_col == "vacc_any_record_dat":
            uptake_inv = invert_df(uptake)
            uptake2_inv = invert_df(uptake_w2)
            out_path = f"{base_path}/all/unreached"
            os.makedirs(out_path, exist_ok=True)
            uptake_inv.to_csv(f"{out_path}/all_unreached_by_group.csv")
            uptake2_inv.to_csv(f"{out_path}/all_unreached_by_group2.csv")

        # For each wave, compute uptake by column
        for wave in range(1, 9 + 1):
            group_type=""
            compute_uptake_for_wave(cohort, wave, cols, event_col, key, group_type, base_path, dir_path)
        for wave2 in range(1, 3 + 1):
            group_type = "2"
            compute_uptake_for_wave(cohort, wave2, cols, event_col, key, group_type, base_path, dir_path)


def compute_uptake_for_wave(cohort, wave, cols, event_col, key, group_type, base_path, dir_path):
    os.makedirs(dir_path, exist_ok=True)
    wave_cohort = cohort[cohort[f"wave{group_type}"] == wave]

    for col in cols:
        dir_path = f"{base_path}/group{group_type}_{wave}/{key}"
        os.makedirs(dir_path, exist_ok=True)
        uptake = compute_uptake(wave_cohort, event_col, col)
        if uptake is None:
            continue
        uptake.to_csv(f"{dir_path}/group_{wave}_{key}_by_{col}.csv")

        if event_col == "vacc_any_record_dat":
            uptake2 = invert_df(uptake)
            out_path = f"{base_path}/group{group_type}_{wave}/unreached"
            os.makedirs(out_path, exist_ok=True)
            uptake2.to_csv(f"{out_path}/group_{wave}_unreached_by_{col}.csv")

if __name__ == "__main__":
    run()
