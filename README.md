# Matching French addresses

## Description

This project, in partnership with the Ministry of Ecological Transition and Territorial Cohesion, aims to standardise French addresses thanks to Machine Learning modelling.

## Requirements

Python 3.8

## Quick start

```shell
git clone https://github.com/alannagenin/french-address-matching.git
cd french-address-matching
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```


```bash
python3 main.py --help
# Usage: main.py [OPTIONS] BUCKET CSV_FILE ADDRESSES_COL CITIES_COL
#                POSTAL_CODE_COL CITY_CODE_COL

# Options:
#   --steps                   Task to perform: "create_sample", "hc", "hmm", "auto"
#   --size INTEGER            Sample size. If steps = create_sample
#   --correct_addresses TEXT  Column containing corrected addresses.
#   --help                    Show this message and exit.
```

```bash
# create a sample using the complete file
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --steps create_sample --size 1000
```

```bash
# hcc perform only hard-coded rules
python3 main.py projet-pfe-adress-matching sample.csv adresse commune cp_corr CODGEO_2021 --steps auto
```
```bash
# hmm only perform HMM (Hidden Markov Model)
python3 main.py projet-pfe-adress-matching sample.csv adresse commune cp_corr CODGEO_2021 --steps auto
```

```bash
# auto use hcc (hard coded rules) and hmm after if the hcc result is considered incorrect for an address
python3 main.py projet-pfe-adress-matching sample.csv adresse commune cp_corr CODGEO_2021 --steps auto
```

By defaut, `--correct_addresses` is set to adresse_corr.

```bash
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --correct_addresses adresse_corr
```


## Contributors

* Alanna Devlin-Génin
* Camille Le Potier