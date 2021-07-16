import pandas as pd
from groups import groups, at_risk_groups

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
            df_out[c] = df_out[c].astype(int)
        else:
            df_out[f"{c} (% of total)"] = df_out[c].astype(int).astype(str) + " (" + df_out[f"{c}_percent"].round(2).astype(str) + "%)" 
            df_out.drop([c, f"{c}_percent"], 1, inplace=True)
        
    print(df_out)
    df_out.to_csv(f'{base_path}/wave_{wave}_summary.csv', float_format='%.2f')