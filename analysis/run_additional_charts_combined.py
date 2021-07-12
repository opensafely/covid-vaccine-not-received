from custom_operations import declined_vaccinated
from plot_practice_charts import *
import pandas as pd

backend = "combined"
base_path = f"released_outputs/{backend}"
start_date = "2020-12-08"
end_date = "2021-05-25"

# load data and set index
df1 = pd.read_csv(base_path+"/additional_figures/practice_list_size_decline_per_1000.csv", index_col=0)
df2 = pd.read_csv(base_path+"/additional_figures/practice_list_size_decline_per_1000_vacc.csv", index_col=0)

# convert summed counts to proportions
df1["decline_per_1000"] = df1["decline_per_1000"]/df1["decline_per_1000"].sum()
df2["decline_per_1000_vacc"] = df2["decline_per_1000_vacc"]/df2["decline_per_1000_vacc"].sum()

df1["decline_per_1000_cumsum"] = df1.cumsum()
df2["decline_per_1000_vacc_cumsum"] = df2.cumsum()

# combine dfs into a dict
dfs ={"decline_per_1000": df1,
      "decline_per_1000_vacc": df2}

# create practice charts
plot_hist(dfs=dfs, output_dir=base_path+"/additional_figures")

# create summary chart of patients declining then accepting vaccines, by priority group
declined_vaccinated()
