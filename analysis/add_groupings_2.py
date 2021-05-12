import numpy as np
import pandas as pd


def add_groupings_2(row):
    row["vacc_group"] = add_vacc_group(row)
    row["decline_group"] = add_decline_group(row)
    row["decline_total_group"] = add_decline_total_group(row)
    row["declined_accepted_group"] = add_declined_accepted_group(row)
    row["vaccinated_and_declined_group"] = add_vacc_and_declined_group(row)
    row["other_reason_group"] = add_other_reason_group(row)
    row["immuno_group"] = add_immuno_group(row)
    row["ckd_group"] = add_ckd_group(row)
    row["ast_group"] = add_ast_group(row)
    row["cns_group"] = add_cns_group(row)
    row["resp_group"] = add_resp_group(row)
    row["bmi_group"] = add_bmi_group(row)
    row["diab_group"] = add_diab_group(row)
    row["sevment_group"] = add_sevment_group(row)
    row["atrisk_group"] = add_atrisk_group(row)
    row["covax1d_group"] = add_covax1d_group(row)
    row["covax2d_group"] = add_covax2d_group(row)
    row["unstatvacc1_group"] = add_unstatvacc1_group(row)
    row["unstatvacc2_group"] = add_unstatvacc2_group(row)
    row["shield_group"] = add_shield_group(row)
    row["preg_group"] = add_preg_group(row)

# Patients with a vaccination
def add_vacc_group(row):
    if row["vacc1_dat"] or row["vacc2_dat"]:
        return True
    else:
        return False

# Patients with a decline (but no vaccination - already incorporated in decl_date)
def add_decline_group(row):
    if row["decl_dat"]:
        return True
    else:
        return False

# Patients with a decline (irrespective of vaccination status)
def add_decline_total_group(row):
    if row["decl_first_dat"]:
        return True
    else:
        return False

# Patients with a decline and a later vaccination
def add_declined_accepted_group(row):
    # check that declined date is within the vaccination campaign period not in the past
    # (otherwise exclude, as unable determine correct sequence of events)
    if gt(row["vacc1_dat"], row["decl_first_dat"]) and (
       row["decl_first_dat"] >= "2020-12-08") and (
       row["vacc1_dat"] >= "2020-12-08"
       ):
        return True
    else:
        return False

# Any other patients with both a decline and a vaccination (but first vaccine did not follow first decline)
def add_vacc_and_declined_group(row):
    if row["decline_total_group"] and row["vacc_group"] and not row["declined_accepted_group"]:
        return True
    else:
        return False

# Patients with any other record related to vaccination (and no vaccination or decline)
def add_other_reason_group(row):    
    ## indicates an attempt or intention to vaccinate but 
    ## (apparently) unsuccessful for reasons other than declining
    if (row["covnot_dat"] or row["covnot_imms_dat"]) and (
        not row["vacc1_dat"]) and not row["decl_dat"]:
        return True
    else:
        return False

def add_immuno_group(row):
    # IF IMMRX_DAT <> NULL     | Select | Next
    if row["immrx_dat"]:
        return True

    # IF IMMDX_COV_DAT <> NULL | Select | Reject
    if row["immdx_cov_dat"]:
        return True
    else:
        return False


def add_ckd_group(row):
    # IF CKD_COV_DAT <> NULL (diagnoses) | Select | Next
    if row["ckd_cov_dat"]:
        return True

    # IF CKD15_DAT = NULL  (No stages)   | Reject | Next
    if not row["ckd15_dat"]:
        return False

    # IF CKD35_DAT>=CKD15_DAT            | Select | Reject
    if gte(row["ckd35_dat"], row["ckd15_dat"]):
        return True
    else:
        return False


def add_ast_group(row):
    # IF ASTADM_DAT <> NULL | Select | Next
    if row["astadm_dat"]:
        return True

    # IF AST_DAT <> NULL    | Next   | Reject
    if not row["ast_dat"]:
        return False

    # IF ASTRXM1 <> NULL    | Next   | Reject
    if not row["astrxm1_dat"]:
        return False

    # IF ASTRXM2 <> NULL    | Next   | Reject
    if not row["astrxm2_dat"]:
        return False

    # IF ASTRXM3 <> NULL    | Select | Reject
    if row["astrxm3_dat"]:
        return True
    else:
        return False


def add_cns_group(row):
    # IF CNS_COV_DAT <> NULL | Select | Reject
    if row["cns_cov_dat"]:
        return True
    else:
        return False


def add_resp_group(row):
    # IF AST_GROUP <> NULL    | Select | Next
    if row["ast_group"]:
        return True

    # IF RESP_COV_DAT <> NULL | Select | Reject
    if row["resp_cov_dat"]:
        return True
    else:
        return False


def add_bmi_group(row):
    # IF SEV_OBESITY_DAT > BMI_DAT | Select | Next
    if gt(row["sev_obesity_dat"], row["bmi_dat"]):
        return True

    # IF BMI_VAL >=40              | Select | Reject
    if gte(row["bmi_val"], 40):
        return True
    else:
        return False


def add_diab_group(row):
    # IF DIAB_DAT > DMRES_DAT | Select | Reject
    if gt(row["diab_dat"], row["dmres_dat"]):
        return True
    else:
        return False


def add_sevment_group(row):
    # IF SEV_MENTAL_DAT > SMHRES_DAT | Select | Reject
    if gt(row["sev_mental_dat"], row["smhres_dat"]):
        return True
    else:
        return False


def add_atrisk_group(row):
    # IF IMMUNOGROUP <> NULL   | Select | Next
    if row["immuno_group"]:
        return True

    # IF CKD_GROUP <> NULL     | Select | Next
    if row["ckd_group"]:
        return True

    # IF RESP_GROUP <> NULL    | Select | Next
    if row["resp_group"]:
        return True

    # IF DIAB_GROUP <> NULL    | Select | Next
    if row["diab_group"]:
        return True

    # IF CLD_DAT <>NULL        | Select | Next
    if row["cld_dat"]:
        return True

    # IF CNS_GROUP <> NULL     | Select | Next
    if row["cns_group"]:
        return True

    # IF CHD_COV_DAT <> NULL   | Select | Next
    if row["chd_cov_dat"]:
        return True

    # IF SPLN_COV_DAT <> NULL  | Select | Next
    if row["spln_cov_dat"]:
        return True

    # IF LEARNDIS_DAT <> NULL  | Select | Next
    if row["learndis_dat"]:
        return True

    # IF SEVMENT_GROUP <> NULL | Select | Reject
    if row["sevment_group"]:
        return True
    else:
        return False


def add_covax1d_group(row):
    # IF COVRX1_DAT <> NULL  | Select | Next
    if row["covrx1_dat"]:
        return True

    # IF COVADM1_DAT <> NULL | Select | Reject
    if row["covadm1_dat"]:
        return True
    else:
        return False


def add_covax2d_group(row):
    # IF COVAX1D_GROUP <> NULL | Next   | Reject
    if not row["covax1d_group"]:
        return False

    # IF COVRX2_DAT <> NULL    | Select | Next
    if row["covrx2_dat"]:
        return True

    # IF COVADM2_DAT <> NULL   | Select | Reject
    if row["covadm2_dat"]:
        return True
    else:
        return False


def add_unstatvacc1_group(row):
    # IF COVAX1D_GROUP <> NULL | Next   | Reject
    if not row["covax1d_group"]:
        return False

    # IF AZD1RX_DAT <> NULL    | Reject | Next
    if row["azd1rx_dat"]:
        return False

    # IF PFD1RX_DAT <> NULL    | Reject | Next
    if row["pfd1rx_dat"]:
        return False

    # IF MOD1RX_DAT <> NULL    | Reject | Next
    if row["mod1rx_dat"]:
        return False

    # IF NXD1RX_DAT <> NULL    | Reject | Next
    if row["nxd1rx_dat"]:
        return False

    # IF JND1RX _DAT <> NULL   | Reject | Next
    if row["jnd1rx_dat"]:
        return False

    # IF GSD1RX_DAT <> NULL    | Reject | Next
    if row["gsd1rx_dat"]:
        return False

    # IF VLD1RX_DAT <> NULL    | Reject | Select
    if row["vld1rx_dat"]:
        return False
    else:
        return True


def add_unstatvacc2_group(row):
    # IF COVAX2D_GROUP <> NULL | Next   | Reject
    if not row["covax2d_group"]:
        return False

    # IF AZD2RX_DAT <> NULL    | Reject | Next
    if row["azd2rx_dat"]:
        return False

    # IF PFD2RX_DAT <> NULL    | Reject | Next
    if row["pfd2rx_dat"]:
        return False

    # IF MOD2RX_DAT <> NULL    | Reject | Next
    if row["mod2rx_dat"]:
        return False

    # IF NXD2RX_DAT <> NULL    | Reject | Next
    if row["nxd2rx_dat"]:
        return False

    # IF JND2RX _DAT <> NULL   | Reject | Next
    if row["jnd2rx_dat"]:
        return False

    # IF GSD2RX_DAT <> NULL    | Reject | Next
    if row["gsd2rx_dat"]:
        return False

    # IF VLD2RX_DAT <> NULL    | Reject | Select
    if row["vld2rx_dat"]:
        return False
    else:
        return True


def add_shield_group(row):
    # IF SHIELD_DAT = NULL                           | Reject | Next
    if not row["shield_dat"]:
        return False

    # IF SHIELD_DAT <> NULL AND NONSHIELD_DAT = NULL | Select | Next
    if row["shield_dat"] and not row["nonshield_dat"]:
        return True

    # IF SHIELD_DAT > NONSHIELD_DAT                  | Select | Reject
    if gt(row["shield_dat"], row["nonshield_dat"]):
        return True
    else:
        return False


def add_preg_group(row):
    # IF PREG_DAT<> NULL        | Next   | Reject
    if not row["preg_dat"]:
        return False

    # IF PREGDEL_DAT > PREG_DAT | Reject | Select
    if gt(row["pregdel_dat"], row["preg_dat"]) and row["sex"]=="F" and int(row["age"])<50:
        return False
    else:
        return True


def gt(lhs, rhs):
    if not lhs:
        return False

    if not rhs:
        return True

    return lhs > rhs


def gte(lhs, rhs):
    if not lhs:
        return False

    if not rhs:
        return True

    if isinstance(rhs, int):
        lhs = float(lhs)

    return lhs >= rhs
