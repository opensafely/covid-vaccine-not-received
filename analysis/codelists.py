from cohortextractor import codelist_from_csv, combine_codelists


# Asthma Diagnosis code
ast = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ast.csv",
    system="snomed",
    column="code",
)

# Asthma Admission codes
astadm = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-astadm.csv",
    system="snomed",
    column="code",
)

# Asthma systemic steroid prescription codes
astrx = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-astrx.csv",
    system="snomed",
    column="code",
)

# Chronic Respiratory Disease
resp_cov = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-resp_cov.csv",
    system="snomed",
    column="code",
)

# Chronic heart disease codes
chd_cov = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-chd_cov.csv",
    system="snomed",
    column="code",
)

# Chronic kidney disease diagnostic codes
ckd_cov = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd_cov.csv",
    system="snomed",
    column="code",
)

# Chronic kidney disease codes - all stages
ckd15 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd15.csv",
    system="snomed",
    column="code",
)

# Chronic kidney disease codes-stages 3 - 5
ckd35 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd35.csv",
    system="snomed",
    column="code",
)

# Chronic Liver disease codes
cld = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-cld.csv",
    system="snomed",
    column="code",
)

# Diabetes diagnosis codes
diab = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-diab.csv",
    system="snomed",
    column="code",
)

# Immunosuppression diagnosis codes
immdx_cov = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-immdx_cov.csv",
    system="snomed",
    column="code",
)

# Immunosuppression medication codes
immrx = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-immrx.csv",
    system="snomed",
    column="code",
)

# Chronic Neurological Disease including Significant Learning Disorder
cns_cov = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-cns_cov.csv",
    system="snomed",
    column="code",
)

# Asplenia or Dysfunction of the Spleen codes
spln_cov = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-spln_cov.csv",
    system="snomed",
    column="code",
)

# BMI
bmi = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-bmi.csv",
    system="snomed",
    column="code",
)

# All BMI coded terms
bmi_stage = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-bmi_stage.csv",
    system="snomed",
    column="code",
)

# Severe Obesity code recorded
sev_obesity = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-sev_obesity.csv",
    system="snomed",
    column="code",
)

# Diabetes resolved codes
dmres = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-dmres.csv",
    system="snomed",
    column="code",
)

# Severe Mental Illness codes
sev_mental = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-sev_mental.csv",
    system="snomed",
    column="code",
)

# Remission codes relating to Severe Mental Illness
smhres = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-smhres.csv",
    system="snomed",
    column="code",
)

# High Risk from COVID-19 code
shield = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-shield.csv",
    system="snomed",
    column="code",
)

# Lower Risk from COVID-19 codes
nonshield = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-nonshield.csv",
    system="snomed",
    column="code",
)

# Wider Learning Disability
learndis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-learndis.csv",
    system="snomed",
    column="code",
)

# First COVID vaccination administration codes - PRIMIS
covadm1_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covadm1.csv",
    system="snomed",
    column="code",
)

# Second COVID vaccination administration codes - PRIMIS
covadm2_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covadm2.csv",
    system="snomed",
    column="code",
)

# Any COVID vaccination administration codes - OpenSafely
covadm_all = codelist_from_csv(
    "codelists/opensafely-covid-19-vaccination-given.csv",
    system="snomed",
    column="code",
)

covadm1 = combine_codelists(
    covadm1_primis,
    covadm_all
)
covadm2 = combine_codelists(
    covadm2_primis,
    covadm_all
)


# Pfizer BioNTech vaccination medication code
pfdrx = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-pfdrx.csv",
    system="snomed",
    column="code",
)

# Oxford AstraZeneca vaccination medication code
azdrx = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-azdrx.csv",
    system="snomed",
    column="code",
)

# Moderna vaccination medication code
modrx = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-modrx.csv",
    system="snomed",
    column="code",
)

# Janssen vaccination medication code
jndrx = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-jndrx.csv",
    system="snomed",
    column="code",
)

# COVID vaccination medication codes
covrx = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covrx.csv",
    system="snomed",
    column="code",
)


# Patients in long-stay nursing and residential care
longres = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-longres.csv",
    system="snomed",
    column="code",
)

# Ethnicity codes
eth2001 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth2001.csv",
    system="snomed",
    column="code",
    category_column="grouping_16_id",
)

# Any other ethnicity code
non_eth2001 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-non_eth2001.csv",
    system="snomed",
    column="code",
)

# Ethnicity not given - patient refused
eth_notgiptref = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth_notgiptref.csv",
    system="snomed",
    column="code",
)

# Ethnicity not stated
eth_notstated = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth_notstated.csv",
    system="snomed",
    column="code",
)

# Ethnicity no record
eth_norecord = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-eth_norecord.csv",
    system="snomed",
    column="code",
)

# Pregnancy or Delivery codes recorded in the 8.5 months before audit run date
pregdel = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-pregdel.csv",
    system="snomed",
    column="code",
)

# Pregnancy codes recorded in the 8.5 months before the audit run date
preg = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-preg.csv",
    system="snomed",
    column="code",
)

# COVID vaccination contraindication codes (PRIMIS list)
covcontra_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covcontra.csv",
    system="snomed",
    column="code",
)
# COVID vaccination contraindication codes (opensafely list)
covcontra_all = codelist_from_csv(
    "codelists/opensafely-covid-19-vaccination-contraindication-or-allergy.csv",
    system="snomed",
    column="code",
)
# COVID vaccination contraindication codes (combined)
covcontra = combine_codelists(
    covcontra_primis,
    covcontra_all
)

# First COVID vaccination declined
cov1decl = codelist_from_csv(
    "codelists/opensafely-covid-19-vaccination-first-dose-declined.csv",
    system="snomed",
    column="code",
)

# Second COVID vaccination declined
cov2decl = codelist_from_csv(
    "codelists/opensafely-covid-19-vaccination-second-dose-declined.csv",
    system="snomed",
    column="code",
)

# First COVID vaccination DNAd
cov1dna = codelist_from_csv(
    "codelists/opensafely-covid-19-vaccination-did-not-attend-first-appointment.csv",
    system="snomed",
    column="code",
)

# Second COVID vaccination DNAd
cov2dna = codelist_from_csv(
    "codelists/opensafely-covid-19-vaccination-did-not-attend-second-appointment.csv",
    system="snomed",
    column="code",
)

# First COVID vaccination not given / not done
cov1notgiven = codelist_from_csv(
    "codelists/opensafely-covid-19-vaccination-first-dose-not-given.csv",
    system="snomed",
    column="code",
)

# Second COVID vaccination not given / not done
cov2notgiven = codelist_from_csv(
    "codelists/opensafely-covid-19-vaccination-second-dose-not-given.csv",
    system="snomed",
    column="code",
)

# COVID vaccination not available
covunav = codelist_from_csv(
    "codelists/opensafely-covid-19-vaccination-unavailable.csv",
    system="snomed",
    column="code",
)


# All codes for vaccine not given (except Declined)
cov2not = combine_codelists(
    cov1dna,
    cov2dna,
    cov1notgiven,
    cov2notgiven,
    covunav,
    covcontra,
)
