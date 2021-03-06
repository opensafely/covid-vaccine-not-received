from comparisons import gt, gte, lt, lte


def add_groupings(df):
    # Patients with a vaccination
    df["vacc_group"] = df["vacc1_dat"].notnull() | df["vacc2_dat"].notnull()

    # Patients with a decline (but no vaccination - already incorporated in decl_date)
    df["decline_group"] = df["decl_dat"].notnull()

    # Patients with a decline (irrespective of vaccination status)
    df["decline_total_group"] = df["decl_first_dat"].notnull() 

    # Patients with a decline and a later vaccination
    # check that declined date is within the vaccination campaign period not in the past
    # (otherwise exclude, as unable determine correct sequence of events)
    df["declined_accepted_group"] =  gt(df["vacc1_dat"], df["decl_first_dat"]) & (
                                     df["decl_first_dat"] >= "2020-12-08") & (
                                     df["vacc1_dat"] >= "2020-12-08"
                                     )

    # Any other patients with both a decline and a vaccination (but first vaccine did not follow first decline)
    df["vaccinated_and_declined_group"] =  df["decline_total_group"] & (
                                           df["vacc_group"]==True) & (
                                           df["declined_accepted_group"]==False
                                           )

    # Patients with any other record related to vaccination (and no vaccination or decline)
    ## indicates an attempt or intention to vaccinate but 
    ## (apparently) unsuccessful for reasons other than declining
    df["other_reason_group"] = (df["covnot_dat"].notnull() | df["covnot_imms_dat"].notnull()) & (
                                df["vacc1_dat"].isnull()) & (df["decl_dat"].isnull())

    # Patients with Immunosuppression
    #
    # IF IMMRX_DAT <> NULL     | Select | Next
    # IF IMMDX_COV_DAT <> NULL | Select | Reject
    df["immuno_group"] = df["immrx_dat"].notnull() | df["immdx_cov_dat"].notnull()

    # Patients with CKD
    #
    # IF CKD_COV_DAT <> NULL (diagnoses) | Select | Next
    # IF CKD15_DAT = NULL  (No stages)   | Reject | Next
    # IF CKD35_DAT>=CKD15_DAT            | Select | Reject
    df["ckd_group"] = df["ckd_cov_dat"].notnull() | (
        df["ckd15_dat"].notnull() & gte(df["ckd35_dat"], df["ckd15_dat"])
    )

    # Patients with Asthma
    #
    # IF ASTADM_DAT <> NULL | Select | Next
    # IF AST_DAT <> NULL    | Next   | Reject
    # IF ASTRXM1 <> NULL    | Next   | Reject
    # IF ASTRXM2 <> NULL    | Next   | Reject
    # IF ASTRXM3 <> NULL    | Select | Reject
    df["ast_group"] = df["astadm_dat"].notnull() | (
        df["ast_dat"].notnull()
        & df["astrxm1_dat"].notnull()
        & df["astrxm2_dat"].notnull()
        & df["astrxm3_dat"].notnull()
    )

    # Patients with CNS Disease (including Stroke/TIA)
    #
    # IF CNS_COV_DAT <> NULL | Select | Reject
    df["cns_group"] = df["cns_cov_dat"].notnull()

    # Patients who have Chronic Respiratory Disease
    #
    # IF AST_GROUP <> NULL    | Select | Next
    # IF RESP_COV_DAT <> NULL | Select | Reject
    df["resp_group"] = df["ast_group"] | df["resp_cov_dat"].notnull()

    # Patients with Morbid Obesity
    #
    # IF SEV_OBESITY_DAT > BMI_DAT | Select | Next
    # IF BMI_VAL >=40              | Select | Reject
    df["bmi_group"] = gt(df["sev_obesity_dat"], df["bmi_dat"]) | (df["bmi_val"] >= 40)

    # Patients with Diabetes
    #
    # IF DIAB_DAT > DMRES_DAT | Select | Reject
    df["diab_group"] = gt(df["diab_dat"], df["dmres_dat"])

    # Patients with Severe Mental Health
    #
    # IF SEV_MENTAL_DAT > SMHRES_DAT | Select | Reject
    df["sevment_group"] = gt(df["sev_mental_dat"], df["smhres_dat"])

    # Patients with Learning disability
    #
    df["learndis_group"] = df["learndis_dat"].notnull()

    # Patients in Any Clinical Risk Group
    #
    # IF IMMUNOGROUP <> NULL   | Select | Next
    # IF CKD_GROUP <> NULL     | Select | Next
    # IF RESP_GROUP <> NULL    | Select | Next
    # IF DIAB_GROUP <> NULL    | Select | Next
    # IF CLD_DAT <>NULL        | Select | Next
    # IF CNS_GROUP <> NULL     | Select | Next
    # IF CHD_COV_DAT <> NULL   | Select | Next
    # IF SPLN_COV_DAT <> NULL  | Select | Next
    # IF LEARNDIS_DAT <> NULL  | Select | Next
    # IF SEVMENT_GROUP <> NULL | Select | Reject
    df["atrisk_group"] = (
        df["immuno_group"]
        | df["ckd_group"]
        | df["resp_group"]
        | df["diab_group"]
        | df["cld_dat"].notnull()
        | df["cns_group"]
        | df["chd_cov_dat"].notnull()
        | df["spln_cov_dat"].notnull()
        | df["learndis_dat"].notnull()
        | df["sevment_group"]
    )

    # Patients who have received at least 1 dose of a COVID Vaccination
    #
    # IF COVRX1_DAT <> NULL  | Select | Next
    # IF COVADM1_DAT <> NULL | Select | Reject
    df["covax1d_group"] = df["covrx1_dat"].notnull() | df["covadm1_dat"].notnull()

    # Patients who have received at least 2 doses of a COVID Vaccination
    #
    # IF COVAX1D_GROUP <> NULL | Next   | Reject
    # IF COVRX2_DAT <> NULL    | Select | Next
    # IF COVADM2_DAT <> NULL   | Select | Reject
    df["covax2d_group"] = df["covax1d_group"] & (
        df["covrx2_dat"].notnull() | df["covadm2_dat"].notnull()
    )

    # Patients who have an unstated dose 1 vaccination type
    #
    # IF COVAX1D_GROUP <> NULL | Next   | Reject
    # IF AZD1RX_DAT <> NULL    | Reject | Next
    # IF PFD1RX_DAT <> NULL    | Reject | Next
    # IF MOD1RX_DAT <> NULL    | Reject | Next
    # IF NXD1RX_DAT <> NULL    | Reject | Next
    # IF JND1RX _DAT <> NULL   | Reject | Next
    # IF GSD1RX_DAT <> NULL    | Reject | Next
    # IF VLD1RX_DAT <> NULL    | Reject | Select
    df["unstatvacc1_group"] = (
        df["covax1d_group"]
        & df["azd1rx_dat"].isnull()
        & df["pfd1rx_dat"].isnull()
        & df["mod1rx_dat"].isnull()
        & df["nxd1rx_dat"].isnull()
        & df["jnd1rx_dat"].isnull()
        & df["gsd1rx_dat"].isnull()
        & df["vld1rx_dat"].isnull()
    )

    # Patients who have an unstated dose 2 vaccination type
    #
    # IF COVAX2D_GROUP <> NULL | Next   | Reject
    # IF AZD2RX_DAT <> NULL    | Reject | Next
    # IF PFD2RX_DAT <> NULL    | Reject | Next
    # IF MOD2RX_DAT <> NULL    | Reject | Next
    # IF NXD2RX_DAT <> NULL    | Reject | Next
    # IF JND2RX _DAT <> NULL   | Reject | Next
    # IF GSD2RX_DAT <> NULL    | Reject | Next
    # IF VLD2RX_DAT <> NULL    | Reject | Select
    df["unstatvacc2_group"] = (
        df["covax2d_group"]
        & df["azd2rx_dat"].isnull()
        & df["pfd2rx_dat"].isnull()
        & df["mod2rx_dat"].isnull()
        & df["nxd2rx_dat"].isnull()
        & df["jnd2rx_dat"].isnull()
        & df["gsd2rx_dat"].isnull()
        & df["vld2rx_dat"].isnull()
    )

    # Patients who are shielding (High Risk from COVID-19)
    #
    # IF SHIELD_DAT = NULL                           | Reject | Next
    # IF SHIELD_DAT <> NULL AND NONSHIELD_DAT = NULL | Select | Next
    # IF SHIELD_DAT > NONSHIELD_DAT                  | Select | Reject
    df["shield_group"] = df["shield_dat"].notnull() & (
        (df["shield_dat"].notnull() & df["nonshield_dat"].isnull())
        | gt(df["shield_dat"], df["nonshield_dat"])
    )

    # Patients who are pregnant
    #
    # IF PREG_DAT<> NULL        | Next   | Reject
    # IF PREGDEL_DAT > PREG_DAT | Reject | Select
    df["preg_group"] = df["preg_dat"].notnull() & lte(df["pregdel_dat"], df["preg_dat"]) & (
                        df["sex"]=="F") & (df["age"]<50
                        )

