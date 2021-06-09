from generate_paper_outputs import run
import os

backend = "combined"
base_path = f"released_outputs/{backend}"
start_date = "2020-12-08"
end_date = "2021-05-25"

# create cumulative charts
run(base_path, start_date, end_date)


