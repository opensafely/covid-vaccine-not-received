import os
import pandas as pd


input_path="output/cohort.pickle"
backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
output_path = "output/" + backend + "/tables"
os.makedirs(output_path, exist_ok=True)

cohort = pd.read_pickle(input_path)


def count_prevalences(cohort):

    for group_type in ["","2"]:
        
        pop_total = cohort["patient_id"].count()
        
        cols = ["vacc_group", "decline_group","decline_total_group",
        "other_reason_group", "declined_accepted_group", "vaccinated_and_declined_group",
        "preg_group", "sevment_group", "learndis_group", "immuno_group"]
        
        prevalences = pd.DataFrame(
            {"total": cohort.groupby([f"wave{group_type}"])["patient_id"].count()}
        )

        
        for col in cols:
            prevalences[col] = (
                cohort[cohort[col]].groupby([f"wave{group_type}"])["patient_id"].count()
            )

        totals = cohort[cols].sum()
        totals["total"] = pop_total
        totals = totals.rename("total")
        prevalences = prevalences.append(totals)

        for high_level_ethnicity_category in [1, 2, 3, 4, 5, 6]:
            prevalences[f"ethnicity_{high_level_ethnicity_category}"] = (
                cohort[cohort["high_level_ethnicity"] == high_level_ethnicity_category]
                .groupby([f"wave{group_type}"])["patient_id"]
                .count()
            )

            eth_total = (
                cohort[cohort["high_level_ethnicity"] == high_level_ethnicity_category]
                ["patient_id"].count()
            )

            prevalences[f"ethnicity_{high_level_ethnicity_category}"].loc["total"] = eth_total

        prevalences.fillna(0, inplace=True)
        prevalences = ((prevalences // 7) * 7).astype(int)

        for c in prevalences.columns:
            prevalences[f"{c}_percent"] = (100*prevalences[c]/prevalences["total"]).round(1)
        prevalences.fillna(0, inplace=True)
        prevalences.to_csv(output_path+f"/prevalences{group_type}.csv")


count_prevalences(cohort)
