from generate_paper_outputs import run
import os

backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
base_path = f"output/{backend}"
start_date = "2020-12-01"
end_date = "2021-05-20"

# create cumulative charts
run(base_path, start_date, end_date)


