import os
import pandas as pd
from transform_fast import load_raw_cohort

input_path="output/cohort.pickle"
output_path="output/cohort_pickle_checks.csv"
backend = os.getenv("OPENSAFELY_BACKEND", "expectations")


cohort = pd.read_pickle(input_path)

if backend=="expectations":
    cohort_s = pd.read_pickle("output/cohort_slow.pickle")

    for col in cohort.columns:
        print (col)
        if "_group" not in col:
            print (cohort[col].count(), cohort_s[col].count())

        else:
            print (cohort[col].sum(), cohort_s[col].sum())

        if col =="decl_first_dat":
            print (cohort.groupby([col]).count(), cohort_s.groupby([col]).count())


#checks = cohort.agg({"max","min", "count"}).transpose()

#checks.to_csv(f"{output_path}")
#print(cohort_s.head().transpose())