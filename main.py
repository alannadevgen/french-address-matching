from standardization.tokens import *
from standardization.import_csv import import_csv
import pandas as pd
from random import sample

if __name__ == '__main__':
    BUCKET = 'projet-pfe-adress-matching'
    FILE_KEY_S3 = 'DonneesCompletes.csv'

    # import of the data
    df_complet = import_csv(BUCKET, FILE_KEY_S3)
    remp_file = pd.read_csv('remplacement.csv', sep=",")
    lib_voie = pd.read_csv('libvoie.csv', sep=",")

    df = df_complet.iloc[:, :8]

    # extract addresses column
    adresse = df.iloc[:, 0]

    sample = adresse.sample(1000)
    sample.to_csv("sample.csv")

    # create tokens for the 100 first addresses
    ex = [['3', '7B', 'GRANDE', 'RUE', 'DU', '14', 'JUILLET', 'PAVILON', '4', 'ET', '6', 'AA', '1234', 'F0', '123']]
    tokens = make_tokens(sample, remp_file=remp_file)
    # frequent = most_frequent_tokens(tokens, 300)
    # print(tokens[0:1000])
    # print(frequent)

    tags = make_tags(tokens, lib_voie)
    print(tags)

    df = df_tags(tags)
    df.to_csv("df.csv")