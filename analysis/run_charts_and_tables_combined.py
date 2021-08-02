'''This module creates the cumulative line charts of vaccines/declines for each cohort, broken down by various factors,
and stacked bar charts of vaccines/declines broken down by certain factors. 

Additionally compiles selected tables together into single summary tables, e.g. to show each wave broken down by ethncity. '''

from generate_paper_outputs import run
import pandas as pd
import glob
from groups import groups, at_risk_groups
from config_for_combined_outputs import base_path, start_date, end_date

# create cumulative charts
run(base_path, start_date, end_date)


def other_table_combinations():
    combine_multiple_waves()
    combine_multiple_waves(breakdown="imd_band",
                        ix=["Unknown","1 (most deprived)","2","3","4","5 (least deprived)"])     

    summary_tables()   


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

    for wave in ['1','2','3']:
        # (combined waves  '1':'65+', '2':'CEV/At Risk', '3':'50-64')
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

other_table_combinations()