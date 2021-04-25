import os
import pandas as pd
from transform_fast import load_raw_cohort

input_path="output/cohort.pickle"
output_path="output/cohort_pickle_checks.csv"
backend = os.getenv("OPENSAFELY_BACKEND", "expectations")


cohort = pd.read_pickle(input_path)

checks = cohort.agg({"max","min", "count"}).transpose()

checks.to_csv(f"{output_path}")
