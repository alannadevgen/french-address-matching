# French address parser :house:

## Description

This project, in partnership with the [Ministry of Ecological Transition and Territorial Cohesion](https://www.ecologie.gouv.fr/), aims to standardise French addresses thanks to Machine Learning modelling.

## Requirements :snake:

This project is deployed using [Python 3.8](https://www.python.org/).

## Quick start

```bash
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
#   --steps                   Task to perform: "create_sample", "hc", "hmm", "auto" (default "auto")
#   --size INTEGER            Sample size. If steps = create_sample (default 1000)
#   --correct_addresses TEXT  Column containing corrected addresses (default "adresse_corr")
#   --result_folder           Name of the folder where put the results (default "result")
#   --recompute_train         Boolean indicating if the model should be reestimated (default False)
#   --help                    Show this message and exit.
```

```bash
# standardize addresses with default arguments for the addresses of the file sample.csv
# important to give the name of the column :
# ADDRESSES_COL=adresse
# CITIES_COL=commune
# POSTAL_CODE_COL=cp_corr
# CITY_CODE_COL=CODGEO_2021     (INSEE code)
python3 main.py projet-pfe-adress-matching sample.csv adresse commune cp_corr CODGEO_2021
```

Create a sample of size 100 using the entire file of addresses.

```bash
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --steps create_sample --size 100
```

Perform only hard-coded rules using the `hc` option.
```bash
python3 main.py projet-pfe-adress-matching sample.csv adresse commune cp_corr CODGEO_2021 --steps hc
```

Only perform HMM (Hidden Markov Model) thanks to the `hmm` option.

```bash
python3 main.py projet-pfe-adress-matching sample.csv adresse commune cp_corr CODGEO_2021 --steps hmm
```

`auto`: use `hc` (hard coded rules) and `hmm` after if the hard-coded result is considered as incorrect for a given address (option by default).

```bash
python3 main.py projet-pfe-adress-matching sample.csv adresse commune cp_corr CODGEO_2021 --steps auto
```

By defaut, `--correct_addresses` is set to adresse_corr.

```bash
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --correct_addresses adresse_corr
```

Recompute the model:
```bash
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --recompute_model True
```

## Contributors :woman_technologist:

<a href="https://github.com/alannagenin/french-address-matching/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=alannagenin/french-address-matching" />
</a>