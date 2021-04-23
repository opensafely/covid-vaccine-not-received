from generate_paper_outputs import run
from custom_operations import practice_variation, current_variation

base_path = f"output/expectations"
start_date = "2020-12-01"
end_date = "2021-04-14"

# create cumulative charts
run(base_path, start_date, end_date)


# create practice charts
practice_variation()

# create summary chart of patient vaccine statuses by priority group
current_variation()
