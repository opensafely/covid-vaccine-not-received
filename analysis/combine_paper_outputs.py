import glob
import os
import pandas as pd

pd.options.display.float_format = "{:,.2f}".format

from combine_cumsums import combine_cumsums

def run():
    # combine cumulative sums
    # for emis_path in sorted(
    #         glob.glob("released_outputs/emis/cumulative_coverage/*/*/*.csv")
    #     ):
    #     combine(emis_path, cumsums=True)
    # combine other paths
    for emis_path in ["released_outputs/emis/tables/prevalences.csv",
            "released_outputs/emis/additional_figures/practice_decline_summary.csv"]:
        combine(emis_path, cumsums=False)
    for emis_path in (
        glob.glob("released_outputs/emis/additional_figures/practice_list_size*.csv")):
        combine(emis_path, cumsums=False)
    for emis_path in (
        glob.glob("released_outputs/emis/tables/wave_*_declined_high_level_ethnicity.csv")
        ):
        combine(emis_path, cumsums=False)        


def combine(emis_path, cumsums=True):
    print(emis_path)
    tpp_path = emis_path.replace("/emis/", "/tpp/")
    emis_df = pd.read_csv(emis_path, index_col=0)
    tpp_df = pd.read_csv(tpp_path, index_col=0)
    if cumsums==True:
        combined_df = combine_cumsums(emis_df, tpp_df)
    else:
        combined_df = emis_df + tpp_df
    for col in combined_df.columns: ### recalculate any percentages
        if "_percent" in col:
            count_col = col.replace("_percent", "")
            combined_df[col] = (100*combined_df[count_col]/combined_df["total"]).round(1)
    combined_path = emis_path.replace("/emis/", "/combined/")
    os.makedirs(os.path.dirname(combined_path), exist_ok=True)
    combined_df.to_csv(combined_path)

    # create table of percent declined by ethnicity across all cohorts
    df = pd.DataFrame(index=["White","Mixed","South Asian", "Black", "Other", "Unknown"])
    for path in sorted(
                glob.glob("released_outputs/combined/tables/wave_*_declined_high_level_ethnicity.csv")
        ):
        pos = path.find("wave_")
        group = path[pos+5:pos+6]
        df1 = pd.read_csv(path).set_index("Unnamed: 0").rename(columns={"Declined_percent":group})

        df = df.join(df1[[group]])
    print(df.head())
    df.to_csv("released_outputs/combined/tables/waves_1_9_declined_high_level_ethnicity.csv")


run()