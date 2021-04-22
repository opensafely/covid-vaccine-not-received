from generate_paper_outputs import run
from custom_operations import practice_variation

base_path = f"output/expectations"
start_date = "2020-12-01"
end_date = "2021-04-14"

# create cumulative charts
run(base_path, start_date, end_date)


# create practice charts
backend, fig = practice_variation()
  
fig.savefig(f"output/{backend}/declines_by_practice_hist.png")

