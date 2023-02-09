from standardization.tokenization import *
from standardization.tagging import *
from utils.csv_io import *
import pandas as pd
from random import sample

if __name__ == '__main__':
    BUCKET = 'projet-pfe-adress-matching'
    FILE_KEY_S3 = 'DonneesCompletes.csv'

    # import the datasets
    df_complet = import_csv(BUCKET, FILE_KEY_S3)
    replacement = pd.read_csv('remplacement.csv', sep=",")
    lib_voie = pd.read_csv('libvoie.csv', sep=",")

    df = df_complet.iloc[:, :8]

    # extract addresses column
    adresse = df.iloc[:, 0]

    sample = adresse.sample(10000)
    # sample.to_csv("sample.csv")

    # create tokens for the 100 first addresses
    tokens = tokenize(sample,replacement_file=replacement)
    
    # frequent = most_frequent_tokens(tokens, 100)
    # print(frequent)

    tags = tag(tokens, libvoie_file=lib_voie)

    df = df_tags(tags)
    # df.to_csv('train.csv', index=False)
    # test
    FILE_KEY_S3_b = "train.csv"
    export_csv(df, BUCKET, FILE_KEY_S3_b)

