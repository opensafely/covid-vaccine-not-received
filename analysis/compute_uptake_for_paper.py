import os
import pandas as pd

from compute_uptake import compute_uptake
from groups import at_risk_groups


demographic_cols = [
    "sex",
    "ethnicity",
    "high_level_ethnicity",
    "imd_band",
]
at_risk_cols = ["atrisk_group"] #+ list(at_risk_groups)
other_cols = ["shield_group", "bmi_group", "preg_group"]

cols = demographic_cols + at_risk_cols + other_cols


def run(input_path="output/cohort.pickle", output_dir="output"):
    backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
    base_path = f"{output_dir}/{backend}/cumulative_coverage"
    cohort = pd.read_pickle(input_path)

    for event_col, key in [
        ("vacc1_dat", "dose_1"),
        ("vacc_anyrecord_dat", "any_vaccine_record"),
        ("decl_dat", "declined"),
        ("cov2not_dat", "vaccine_not_done"),
	    ("cov1decl_acc_dat", "declined_accepted"),
    ]:
        # Compute uptake by wave
        dir_path = f"{base_path}/all/{key}"
        os.makedirs(dir_path, exist_ok=True)
        uptake = compute_uptake(cohort, event_col, "wave")
        uptake.to_csv(f"{dir_path}/all_{key}_by_group.csv")

        # For each wave, compute uptake by column
        for wave in range(1, 9 + 1):
            os.makedirs(dir_path, exist_ok=True)
            wave_cohort = cohort[cohort["wave"] == wave]
            for col in cols:
                dir_path = f"{base_path}/group_{wave}/{key}"
                os.makedirs(dir_path, exist_ok=True)
                uptake = compute_uptake(wave_cohort, event_col, col)
                if uptake is None:
                    continue
                uptake.to_csv(f"{dir_path}/group_{wave}_{key}_by_{col}.csv")


if __name__ == "__main__":
    run()
