import glob
import os
import pandas as pd
import numpy as np

pd.options.display.float_format = "{:,.2f}".format

from combine_cumsums import combine_cumsums

def run():
    # combine cumulative sums
    for emis_path in sorted(
          glob.glob("released_outputs/emis/cumulative_coverage/*/*/*.csv")
      ):
       combine(emis_path, cumsums=True)

    # combine other files
    for emis_path in ["released_outputs/emis/tables/prevalences.csv",
            "released_outputs/emis/additional_figures/practice_decline_summary.csv",
            "released_outputs/emis/additional_figures/declined_then_accepted.csv"]:
        combine(emis_path, cumsums=False)

    for emis_path in ["released_outputs/emis/additional_figures/declined_then_accepted_by_wave.csv",
            "released_outputs/emis/additional_figures/declined_accepted_weeks_by_wave.csv"]:
        combine(emis_path, cumsums=False, indices=2)

    for emis_path in (
        glob.glob("released_outputs/emis/additional_figures/practice_list_size*.csv")):
        combine(emis_path, cumsums=False)
    

    combine_multiple_waves()
    combine_multiple_waves(breakdown="imd_band",
                        ix=["Unknown","1 (most deprived)","2","3","4","5 (least deprived)"])        


def combine(emis_path, cumsums=True, indices=1):
    print(emis_path)
    tpp_path = emis_path.replace("/emis/", "/tpp/")

    indices = np.arange(0,indices)

    emis_df = pd.read_csv(emis_path, index_col=indices)
    tpp_df = pd.read_csv(tpp_path, index_col=indices)
    if cumsums==True:
        combined_df = combine_cumsums(emis_df, tpp_df)
    else:
        combined_df = emis_df + tpp_df

    if "declined_accepted_weeks" in emis_path: # calculate rates
        combined_df = combined_df.unstack()
        combined_df.columns = combined_df.columns.droplevel()
        print(combined_df, combined_df.sum())
    
    for col in combined_df.columns: ### recalculate any percentages
        if "_percent" in col:
            count_col = col.replace("_percent", "")
            combined_df[col] = (100*combined_df[count_col]/combined_df["total"]).round(1)
        if "declined_then_accepted" in emis_path: # calculate rates
            combined_df["per_1000"] = (1000*combined_df["Declined then accepted"]/combined_df["total"]).round(2)
            combined_df["per_1000_vacc"] = (1000*combined_df["Declined then accepted"]/combined_df["Vaccinated"]).round(2)
            combined_df["converted"] = (1000*combined_df["Declined then accepted"]/combined_df["Declined - all"]).round(2)
        if "declined_accepted_weeks" in emis_path: # calculate percentages
            combined_df[f"{col}_percent"] = (100*combined_df[col]/combined_df.sum(axis=1)).round(3)

    combined_path = emis_path.replace("/emis/", "/combined/")
    os.makedirs(os.path.dirname(combined_path), exist_ok=True)
    combined_df.to_csv(combined_path)

def combine_multiple_waves(breakdown="high_level_ethnicity",
                            ix=["White","Mixed","South Asian", "Black", "Other", "Unknown"]):
    # create table of percent declined by ethnicity across all cohorts
    base_path = "released_outputs/combined/tables/"

    df = pd.DataFrame(index=ix)

    for path in sorted(
                glob.glob(f"{base_path}wave_*_declined_{breakdown}.csv")
        ):
        print(path)
        pos = path.find("wave_")
        group = path[pos+5:pos+6]
        df1 = pd.read_csv(path).set_index("Unnamed: 0").rename(columns={"Declined_percent":group})

        df = df.join(df1[[group]])
    df.to_csv(f"{base_path}waves_1_9_declined_{breakdown}.csv")

run()