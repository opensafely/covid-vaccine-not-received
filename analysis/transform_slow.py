import csv
from tempfile import NamedTemporaryFile

import pandas as pd

from age_bands import age_bands
from add_groupings_2 import add_groupings_2
from transform_fast import extra_at_risk_cols, extra_vacc_cols, necessary_cols

necessary_cols.extend(["cov1decl_dat", "cov2decl_dat"])

# Get mapping from category (1-16) to high-level category (1-5)
category_to_high_level_category = {}
with open("codelists/primis-covid19-vacc-uptake-eth2001.csv") as f:
    for record in csv.DictReader(f):
        category = int(record["grouping_16_id"])
        high_level_category = int(record["grouping_6_id"])

        if category in category_to_high_level_category:
            assert category_to_high_level_category[category] == high_level_category
        else:
            category_to_high_level_category[category] = high_level_category


def run(input_path="output/input.csv", output_path="output/cohort.pickle"):
    with open(input_path) as f:
        reader = csv.DictReader(f)
        cohort = transform(reader)
    cohort.to_pickle(output_path)


def transform(reader):
    with NamedTemporaryFile("w+") as f:
        writer = csv.DictWriter(f, necessary_cols)
        writer.writeheader()
        for row in transform_rows(reader):
            writer.writerow(row)

        f.seek(0)

        # We set parse_dates and dtype to ensure that the returned dataframe is
        # identical to that returned by the original transform.
        date_fieldnames = [
            fn
            for fn in necessary_cols
            if fn.endswith("_dat") and fn not in extra_vacc_cols
        ]
        dtypes = {
            "ethnicity": "int8",
            "high_level_ethnicity": "int8",
        }
        cohort = pd.read_csv(f.name, parse_dates=date_fieldnames, dtype=dtypes)
    return cohort[necessary_cols]


def transform_rows(rows):
    for ix, row in enumerate(rows):
        if non_fm_sex(row):
            continue
        if over_120_age(row):
            continue
        if under_16_age(row):
            continue

        add_imd_bands(row)
        add_ethnicity(row)
        add_high_level_ethnicity(row)
        add_missing_vacc_columns(row)
        replace_unknown_dates(row)
        add_vacc_dates(row)
        add_earliest_decline_dates(row)
        add_vacc_decline_dates(row)
        add_vacc_any_record_dates(row)
        add_age_bands(row, range(1, 12 + 1))
        add_groupings_2(row)
        add_waves(row)
        add_waves_2(row)
        add_extra_at_risk_cols(row)
        row = {k: v for k, v in row.items() if k in necessary_cols}
        yield row


def non_fm_sex(row):
    """Return True if sex is not F or M."""

    return row["sex"] not in ["F", "M"]


def over_120_age(row):
    """Return True if age is >= 120.

    There are a handful of patients with a recorded date of birth of 1900-01-01.
    """

    return int(row["age"]) >= 120

def under_16_age(row):
    """Return True if age is < 16.

    """

    return int(row["age"]) < 16

def add_imd_bands(row):
    """Add IMD band from 1 (most deprived) to 5 (least deprived), or 0 if missing."""

    if not row["imd"]:
        row["imd_band"] = 0
        return

    for band in range(1, 5 + 1):
        if int(row["imd"]) < band * 32844 / 5:
            row["imd_band"] = band
            return


def add_ethnicity(row):
    """Add ethnicity using bandings from PRIMIS spec."""

    if row["eth2001"]:
        # eth2001 already indicates whether a patient is in any of bands 1-16
        row["ethnicity"] = int(row["eth2001"])

    elif row["non_eth2001_dat"]:
        # Add band 17 (Patients with any other ethnicity code)
        row["ethnicity"] = 17

    elif row["eth_notgiptref_dat"]:
        # Add band 18 (Ethnicity not given - patient refused)
        row["ethnicity"] = 18

    elif row["eth_notstated_dat"]:
        # Add band 19 (Ethnicity not stated)
        row["ethnicity"] = 19

    else:
        # Add band 20 (Ethnicity not recorded)
        row["ethnicity"] = 20


def add_high_level_ethnicity(row):
    """Add high-level ethnicity categories, based on bandings from PRIMIS spec."""

    # Set high_level_ethnicity based on ethnicity column
    row["high_level_ethnicity"] = category_to_high_level_category.get(
        row["ethnicity"], 6  # 6 is "unknown"
    )


def add_missing_vacc_columns(row):
    """Add columns for vaccines that are not yet available but which are referenced by
    the spec.
    """

    for prefix in ["mo", "nx", "jn", "gs", "vl"]:
        assert f"{prefix}d1rx_dat" not in row
        assert f"{prefix}d2rx_dat" not in row
        row[f"{prefix}d1rx_dat"] = ""
        row[f"{prefix}d2rx_dat"] = ""


def replace_unknown_dates(row):
    """Where an event date was unknown (1900-01-01) or obviously incorrect (prior to vaccination campaign),
    replace with "2020-11-28". 
    """
    for col in ["cov1decl_dat", "cov2decl_dat", "covdecl_imms_dat", "covnot_dat", "covnot_imms_dat"]:
        d = row[col]
        
        if (d is not None) & (d != ""):
            if d < "2020-11-29":
                row[col] = "2020-11-28"


def add_vacc_dates(row):
    """Record earliest date of first and second vaccinations.

    In some cases, a patient will have only one covadm1/2_dat and covrx1/2_dat.
    """
    covsnomed_dat = row["covsnomed_dat"]
    for ix in 1, 2:
        covadm_dat = row[f"covadm{ix}_dat"]
        covrx_dat = row[f"covrx{ix}_dat"]
        vacc_dat_fn = f"vacc{ix}_dat"

        if ix==1:
            dates = [covadm_dat, covsnomed_dat, covrx_dat]
        else:
            dates = [covadm_dat, covrx_dat]
            
        actual_dates = [date for date in dates if date]
            
        if actual_dates:
            row[vacc_dat_fn] = min(actual_dates)
        else:
            row[vacc_dat_fn] = ""

def add_earliest_decline_dates(row):
    """Record earliest date of a decline (irrespective of vaccination status).
    """

    dates = [row["cov1decl_dat"], row["cov2decl_dat"], row["covdecl_imms_dat"]]
    actual_dates = [date for date in dates if date]
    
    if actual_dates:
        row["decl_first_dat"] = min(actual_dates)
    else:
        row["decl_first_dat"] = ""


def add_vacc_decline_dates(row):
    """Record decline only if patient has had no vaccine recorded.
    """
    row["decl_dat"] = row["decl_first_dat"]

    # Replace declined date with null if a vaccine has been recorded
    if row["vacc1_dat"]:
        row["decl_dat"] = ""


def add_vacc_any_record_dates(row):
    """Date at which patient went from unvaccinated to vaccinated, 
    OR had any record related to vaccine refusal, contraindications etc. 
    """
    dates = [row["vacc1_dat"], row["vacc2_dat"], row["covnot_dat"], row["covnot_imms_dat"], row["decl_dat"]]
    actual_dates = [date for date in dates if date]
    
    if actual_dates:
        row["vacc_any_record_dat"] =  min(actual_dates)
    else:
        row["vacc_any_record_dat"] = ""


def add_age_bands(row, bands):
    for band in bands:
        lower, upper = age_bands[band]
        if lower is None:
            lower = -1
        if upper is None:
            upper = 999
        if lower <= int(row["age"]) < upper:
            row["age_band"] = band
            return

    assert False


def add_waves(row):
    age = int(row["age"])

    if row["longres_dat"] and age >= 65:
        # Wave 1: Residents in Care Homes
        # (The spec includes staff in care homes, but occupation codes are not well
        # recorded)
        row["wave"] = 1

    elif age >= 80:
        # Wave 2: Age 80 or over
        # (This spec includes frontline H&SC workers, but see above.)
        row["wave"] = 2

    elif 70 <= age <= 79:
        # Wave 3: Age 70 - 79
        row["wave"] = 3

    elif row["shield_group"]:
        # Wave 4: Clinically Extremely Vulnerable
        row["wave"] = 4

    elif 65 <= age <= 69:
        # Wave 5: Age 65 - 69
        row["wave"] = 5

    elif (16 <= age <= 64) and row["atrisk_group"]:
        # Wave 6: Age 16-64 in a defined At Risk group
        row["wave"] = 6

    elif 60 <= age <= 64:
        # Wave 7: Age 60 - 64
        row["wave"] = 7

    elif 55 <= age <= 59:
        # Wave 8: Age 55 - 59
        row["wave"] = 8

    elif 50 <= age <= 54:
        # Wave 9: Age 50 - 54
        row["wave"] = 9

    else:
        row["wave"] = 0


def add_waves_2(row):

    # Wave 2.1: Residents in Care Homes and those over 65 (waves 1-3 & 5)
    if row["wave"] in [1,2,3,5]:
        row["wave2"] = 1

    # Wave 2.2: CEV (aged 16-69) and At Risk (aged 16-64)
    elif row["wave"] in [4,6]:
        row["wave2"] = 2

    # Wave 2.3: 50-64
    elif row["wave"] in [7,8,9]:
        row["wave2"] = 3

    else:
        row["wave2"] = 0

def add_extra_at_risk_cols(row):
    """Add columns for extra at-risk groups."""

    for col in extra_at_risk_cols:
        date_col = col.replace("_group", "_dat")
        if date_col in row:
            row[col] = bool(row[date_col])


if __name__ == "__main__":
    import sys

    run(input_path=sys.argv[1])
