import pandas as pd
import csv
from tempfile import NamedTemporaryFile
from transform_fast import extra_vacc_cols, necessary_cols
from datetime import datetime

# We set parse_dates and dtype to ensure that the returned dataframe is
# identical to that returned by the original transform.
dtypes = {
    "ethnicity": "int8",
    "high_level_ethnicity": "int8",
}

cohort_head = pd.read_csv("output/input.csv", nrows=1)
date_fieldnames = [c for c in cohort_head if c.endswith("_dat")]

cohort = pd.read_csv("output/input.csv", parse_dates=date_fieldnames, dtype=dtypes)



def replace_unknown_dates(row):
    """Where an event date was unknown (1900-01-01) or obviously incorrect (prior to vaccination campaign),
    replace with "2020-11-28". 
    """
    for col in ["cov1decl_dat", "cov2decl_dat", "covdecl_imms_dat", "covnot_dat", "covnot_imms_dat"]:
        d = row[col]
        if d is None:
            pass
        elif (d < datetime(2020,11,28)):
            row[col] = "2020-11-28" #datetime(2020,11,28)



def add_vacc_dates(row):
    """Record earliest date of first and second vaccinations.

    In some cases, a patient will have only one covadm1/2_dat and covrx1/2_dat.
    """

    covsnomed_dat = row["covsnomed_dat"]

    for ix in 1, 2:
        covadm_dat = row[f"covadm{ix}_dat"]
        covrx_dat = row[f"covrx{ix}_dat"]
        vacc_dat_fn = f"vacc{ix}_dat"
        
        x = [covadm_dat, covrx_dat, covsnomed_dat]
        d = pd.Series(x)
        row[vacc_dat_fn] = d.min()

def add_earliest_decline_dates(row):
    """Record earliest date of a decline (irrespective of vaccination status).
    """

    dates = [row["cov1decl_dat"], row["cov2decl_dat"], row["covdecl_imms_dat"]]
    dates = pd.Series(dates)
    
    import pdb; pdb.set_trace()
    row["decl_first_dat"] = dates.min()
        
for index, row in cohort.iterrows():
    #replace_unknown_dates(row)
    add_earliest_decline_dates(row)