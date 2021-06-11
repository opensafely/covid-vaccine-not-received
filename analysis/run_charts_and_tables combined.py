from generate_paper_outputs import run
from generate_extra_combined_charts import plot_grouped_bar
import os

backend = "combined"
base_path = f"released_outputs/{backend}"
start_date = "2020-12-08"
end_date = "2021-05-25"

# create cumulative charts
run(base_path, start_date, end_date)


# plot combined-only charts
plot_grouped_bar(backend=backend, output_dir=base_path, breakdown="high_level_ethnicity")
plot_grouped_bar(backend=backend, output_dir=base_path, breakdown="imd_band")