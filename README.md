# COVID Vaccines "Not Received"
This project investigates the patterns of usage for codes indicative of patients declining a COVID vaccine, in combination with their vaccination status. In the unvaccinated, it also looks at other codes which may indicate a vaccination attempt or unsuitability for vaccination (e.g. contraindication). 


This is the code and configuration for our paper, 'Recording of “COVID-19 vaccine declined” among vaccination priority groups: a cohort study on 57.9 million NHS patients’ primary care records in situ using OpenSAFELY'

* The preprint is [here]()
* Outputs, including charts, and tables, are in `released_outputs/`
* If you are interested in how we defined our variables, take a look at the [study definition](analysis/study_definition.py); this is written in `python`, but non-programmers should be able to understand what is going on there
* If you are interested in how we defined our code lists, look in the [codelists folder](./codelists/).
* Developers and epidemiologists interested in the framework should review [the OpenSAFELY documentation](https://docs.opensafely.org)

# About the OpenSAFELY framework

The OpenSAFELY framework is a secure analytics platform for
electronic health records research in the NHS.

Instead of requesting access for slices of patient data and
transporting them elsewhere for analysis, the framework supports
developing analytics against dummy data, and then running against the
real data *within the same infrastructure that the data is stored*.
Read more at [OpenSAFELY.org](https://opensafely.org).
