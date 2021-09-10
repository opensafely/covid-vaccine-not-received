# COVID Vaccines "Not Received"
This project investigates the patterns of usage for codes indicative of patients declining a COVID vaccine, in combination with their vaccination status. In the unvaccinated, it also looks at other codes which may indicate a vaccination attempt or unsuitability for vaccination (e.g. contraindication). 


This is the code and configuration for our paper, 'Recording of “COVID-19 vaccine declined” among vaccination priority groups: a cohort study on 57.9 million NHS patients’ primary care records in situ using OpenSAFELY'

* The preprint is [here](https://www.medrxiv.org/content/10.1101/2021.08.05.21259863v1) and the paper has been submitted for peer review. 
* Outputs, including charts, and tables, are in `released_outputs/`
* If you are interested in how we defined our variables, take a look at the [study definition](analysis/study_definition.py); this is written in `python`, but non-programmers should be able to understand what is going on there
* If you are interested in how we defined our code lists, look in the [codelists folder](./codelists/).
* Developers and epidemiologists interested in the framework should review [the OpenSAFELY documentation](https://docs.opensafely.org)

# Vaccine priority groups
* Here we use the COVID Vaccine recording specification to identify those who are were in priority groups for the vaccination as determined by records held by GPs (i.e. not including employment status). 
* We regroup slightly such that 70-79s are all grouped together and the Clinically Extremely Vulnerable (CEV) are in a separate cohort. 
* We also use combined groups: 1) over 65s (inc care home residents); 2) CEV/At Risk; 3) 50-64. These are denoted as `group2_N` in outputs

# Data processing
* Data processing files are found in the [analysis](./analysis) folder. 
* Basic criteria are assessed in the study definition, e.g. age, vaccination dates, dates of diagnosis for various conditions. 
* The [transform](./analysis/transform.py) step filters and cleans the data and labels patients with their priority group, other factors of interest, and vaccine status. It converts the original csv produced by the study definition step into a `cohort.pickle` file. A number of other modules are called upon to apply groupings:
  * Clinical groupings (vaccine status, at-risk status etc) are defined in [this file](./analysis/add_groupings.py) e.g. applying AND/OR logic where multiple criteria are to be combined to define a group, or where sequences of events need to be determined. 
  * Age groups and their limits are defined in [this file](./analysis/age_bands.py). 
  * Separate files provide the names/descriptions of each of the [ethnic groups](./analysis/ethnicities.py), [at risk groups](./analysis/age_bands.py)
* The  ['compute uptake'](./analysis/compute_uptake_for_paper.py) step processes the `pickle` file into a series of cumulative incidence files for each event of interest (number of people vaccinated, declined, etc), for each priority group (e.g. 80+), both in total and broken down by each factor of interest (e.g. ethnicity). 
* Other analyses are separately carried out on the `pickle` file [here](./analysis/custom_operations.py), including patients recorded as declining and later being vaccinated, and levels of recording at each practice.

# Federated analysis
* Aggregated cumulative output files are combined from the two different practice EHR systems. After all files are released from both systems, use the following steps to create combined outputs.

* Process
  1. Run `combine_paper_outputs` - this combines data from both backends including the main cumulative data files of vaccines/declines per day, and also other files including practice-level data and data on declines recorded prior to a later vaccination.
  2. Run `run_charts_and_tables combined` - this uses the combined datasets to create cumulative time trend charts, stacked charts, and also some summary tables. 
  3. Run `run_additional_charts_combined` - creates some additional tables and charts, largely using the combined practice-level data to create practice histograms, and the declined-then-vaccinated datasets to make various charts and tables.

# About the OpenSAFELY framework

The OpenSAFELY framework is a secure analytics platform for
electronic health records research in the NHS.

Instead of requesting access for slices of patient data and
transporting them elsewhere for analysis, the framework supports
developing analytics against dummy data, and then running against the
real data *within the same infrastructure that the data is stored*.
Read more at [OpenSAFELY.org](https://opensafely.org).
