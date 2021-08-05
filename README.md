# COVID Vaccines "Not Received"
This project investigates the patterns of usage for codes indicative of patients declining a COVID vaccine, in combination with their vaccination status. In the unvaccinated, it also looks at other codes which may indicate a vaccination attempt or unsuitability for vaccination (e.g. contraindication). 


This is the code and configuration for our paper, 'Recording of “COVID-19 vaccine declined” among vaccination priority groups: a cohort study on 57.9 million NHS patients’ primary care records in situ using OpenSAFELY'

* The preprint is [here]()
* Outputs, including charts, and tables, are in `released_outputs/`
* If you are interested in how we defined our variables, take a look at the [study definition](analysis/study_definition.py); this is written in `python`, but non-programmers should be able to understand what is going on there
* If you are interested in how we defined our code lists, look in the [codelists folder](./codelists/).
* Developers and epidemiologists interested in the framework should review [the OpenSAFELY documentation](https://docs.opensafely.org)

# Vaccine priority groups
* Here we use the COVID Vaccine recording specification to identify those who are were in priority groups for the vaccination as determined by records held by GPs (i.e. not including employment status). 
* We regroup slightly such that 70-79s are all grouped together and the Clinically Extremely Vulnerable (CEV) are in a separate cohort. 
* We also use combined groups: 1) over 65s (inc care home residents); 2) CEV/At Risk; 3) 50-64. These are denoted as `group2_N` in outputs

# Federated analysis
* Aggregated output files are combined from two different practice EHR systems. After all files are released from both systems, use the following steps to create combined outputs.

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
