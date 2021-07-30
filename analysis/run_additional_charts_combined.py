'''This module creates histograms for declines at practice level, and for vaccines declined then received.
'''

from custom_operations import declined_vaccinated
from generate_extra_combined_charts import plot_grouped_bar, plot_simple_bar
from plot_practice_charts import *
import pandas as pd

backend = "combined"
base_path = f"released_outputs/{backend}"
start_date = "2020-12-08"
end_date = "2021-05-25"

# plot combined-only charts: declines broken down by priority group and ethnicity/imd
plot_grouped_bar(backend=backend, output_dir=base_path, breakdown="high_level_ethnicity")
plot_grouped_bar(backend=backend, output_dir=base_path, breakdown="imd_band")

# create summary chart of patients declining then receiving vaccines, by priority group
plot_simple_bar(backend="combined", output_dir=base_path)

# create summary chart of patients declining then receiving vaccines, by priority group and by time or ethnicity
plot_grouped_bar(backend=backend, output_dir=base_path, measure="declined_then_accepted", breakdown="weeks_diff")
plot_grouped_bar(backend=backend, output_dir=base_path, measure="declined_then_accepted", breakdown="high_level_ethnicity")



### Practice charts

# load data and set index
df1 = pd.read_csv(base_path+"/additional_figures/practice_counts_decline_per_1000.csv", index_col=0)
df2 = pd.read_csv(base_path+"/additional_figures/practice_counts_decline_per_1000_vacc.csv", index_col=0)
# for heatmap:
df3 = pd.read_csv(base_path+"/additional_figures/practice_list_size_decline_per_1000.csv", index_col=0)

# convert summed counts to proportions
df1["decline_per_1000"] = df1["decline_per_1000"]/df1["decline_per_1000"].sum()
df2["decline_per_1000_vacc"] = df2["decline_per_1000_vacc"]/df2["decline_per_1000_vacc"].sum()

df1["decline_per_1000_cumsum"] = df1.cumsum()
df2["decline_per_1000_vacc_cumsum"] = df2.cumsum()

# combine dfs into a dict
dfs_hist ={"decline_per_1000": df1,
      "decline_per_1000_vacc": df2}
dfs_heat ={"decline_per_1000": df3}

# create practice charts
plot_hist(dfs=dfs_hist, output_dir=base_path+"/additional_figures")
plot_heatmap(dfs=dfs_heat, output_dir=base_path+"/additional_figures")

# create summary chart of patients declining then accepting vaccines, by priority group
#declined_vaccinated()
