import os
import pandas as pd
from transform_fast import load_raw_cohort
import csv

input_path="output/input.csv"
output_path="output/cohort_checks.csv"
backend = os.getenv("OPENSAFELY_BACKEND", "expectations")

def load_raw_cohort(input_path):
    with open(input_path) as f:
        reader = csv.reader(f)
        fieldnames = next(reader)

    date_fieldnames = [fn for fn in fieldnames if fn.endswith("_dat")]
    raw_cohort = pd.read_csv(input_path, parse_dates=date_fieldnames, usecols=date_fieldnames)
    return raw_cohort

raw_cohort = load_raw_cohort(input_path)

checks = raw_cohort.agg({"max","min"})

checks.to_csv(f"{output_path}")
