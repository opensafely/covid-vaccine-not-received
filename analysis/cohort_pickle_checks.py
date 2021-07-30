''' Run locally to compare outputs from transform_fast and transform_slow (which should be identical)
'''

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
        if "_group" in col: # sum binary flags
            print (cohort[col].sum(), cohort_s[col].sum())

        else: # otherwise count values (mostly dates)
            print (cohort[col].count(), cohort_s[col].count())

        if col =="decl_first_dat":
            print (cohort.groupby([col]).count(), cohort_s.groupby([col]).count())


#checks = cohort.agg({"max","min", "count"}).transpose()

#checks.to_csv(f"{output_path}")
#print(cohort_s.head().transpose())
print (cohort_s.columns == cohort.columns)

cohort_s = cohort_s.reset_index() 
cohort = cohort.reset_index()

print(cohort_s["decl_dat"].head(), cohort["decl_dat"].head())

