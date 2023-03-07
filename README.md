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
# Usage: main.py [OPTIONS]
#
# Options:
#   --create-sample BOOLEAN            Create a new sample of the dataset.
#   --help                             Show this message and exit.
```

By defaut, `--create-sample` is set to False.

```bash
# default values
python3 main.py --create-sample False
# create a new sample for training data
python3 main.py --create-sample True
# all process
python3 main.py projet-pfe-adress-matching DonneesCompletes.csv adresse commune cp_corr CODGEO_2021 --create-sample True
```

## Contributors

* Alanna Devlin-Génin
* Camille Le Potier