''' Combine cumulative coverage tables from EMIS and TPP; 
also combines prevalence figures, practice summaries, and declined-then-received
tables from EMIS and TPP that were derived separately.

Additionally compiles summary files together (that have already been combined between TPP and EMIS),
e.g. to show each wave broken down by ethncity in a single summary table. 
'''

import glob
import os
import pandas as pd
import numpy as np
from groups import groups, at_risk_groups

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

    summary_tables()   


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
            combined_df["per_1000"] = (1000*combined_df["Declined then received"]/combined_df["total"]).round(2)
            combined_df["per_1000_vacc"] = (1000*combined_df["Declined then received"]/combined_df["Vaccinated"]).round(2)
            combined_df["converted"] = (1000*combined_df["Declined then received"]/combined_df["Declined - all"]).round(2)
        if "declined_accepted_weeks" in emis_path: # calculate percentages
            combined_df[f"{col}_percent"] = (100*combined_df[col]/combined_df.sum(axis=1)).round(3)

    combined_path = emis_path.replace("/emis/", "/combined/")
    os.makedirs(os.path.dirname(combined_path), exist_ok=True)
    combined_df.to_csv(combined_path)

def combine_multiple_waves(breakdown="high_level_ethnicity",
                            ix=["White","Mixed","South Asian", "Black", "Other", "Unknown"]):
    # create table of "percent declined" by ethnicity across all cohorts
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


def summary_tables():
    '''create summary table for each of the 3 combined cohorts'''
    base_path = 'released_outputs/combined/tables'

    # create a lookup for group names by combining the two imported dicts
    groups.update(at_risk_groups)
    demographics = {"age_band": "Age Band", 'sex':'Sex', 'high_level_ethnicity': 'High Level Ethnicity', 'imd_band': 'IMD Band'}
    groups.update(demographics)

    for wave in {'1':'65+','2':'CEV/At Risk','3':'50-64'}:
        df_out = pd.DataFrame()
        for key in ['age_band', 'sex', 'high_level_ethnicity', 'imd_band', 'preg_group', 'sevment_group', 'learndis_group']:
            if (key == 'preg_group') & (wave != '2'):
                continue
            elif (wave == '3') & ((key == 'learndis_group') | (key == 'sevment_group')):
                continue
            df = pd.read_csv(f"{base_path}/wave2_{wave}_declined_{key}.csv", index_col=0)
            
            df['Category'] = groups[key]
            df = df.set_index('Category', append=True).swaplevel()
            
            df_out = pd.concat([df_out, df])
        
        for c in ['total', 'Vaccinated','Declined','Contraindicated/unsuccessful','No Records']:
            if c == 'total':
                df_out[c] = df_out[c].astype(int).apply('{:,}'.format)
            else:
                df_out[f"{c} (% of total)"] = df_out[c].astype(int).apply('{:,}'.format) + " (" + df_out[f"{c}_percent"].apply('{:.2f}'.format) + "%)" 
                df_out.drop([c, f"{c}_percent"], 1, inplace=True)
            df_out.to_csv(f'{base_path}/wave2_{wave}_summary.csv', float_format='%.2f')

run()