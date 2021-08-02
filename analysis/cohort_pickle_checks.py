''' Count number of declines with uncertain dates. 
'''

import os
import pandas as pd
import numpy as np

input_path="output/cohort.pickle"
output_path="output/cohort_pickle_checks.csv"
backend = os.getenv("OPENSAFELY_BACKEND", "expectations")

cohort = pd.read_pickle(input_path)

cohort = cohort.loc[pd.notnull(cohort["decl_first_dat"])]
cohort["decline date incorrect"] = np.where(cohort["decl_first_dat"] < "2020-12-08", 1, 0)

checks = cohort.groupby(["decline date incorrect"])["sex"].count()
checks = 100*checks/checks.sum()
print (checks)

#checks = cohort.agg({"max","min", "count"}).transpose()

checks.to_csv(f"{output_path}")


