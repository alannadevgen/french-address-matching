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
#   --create-sample BOOLEAN   Create a new sample of the dataset.
#   --size INTEGER            Sample size.
#   --correct_addresses TEXT  Column containing corrected addresses.
#   --help                    Show this message and exit.
```

```bash
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021
```

By defaut, `--create-sample` is set to False.

```bash
# default values
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --create-sample False
# create a new sample for training data
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --create-sample True
# only perform the creation of the training sample
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --steps train
# only perform the hmm
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --steps hmm
# perform all
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --steps all
```

By defaut, `--correct_addresses` is set to adresse_corr.

```bash
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --correct_addresses adresse_corr
```


## Contributors

* Alanna Devlin-Génin
* Camille Le Potier