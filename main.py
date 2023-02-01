from standardization.tokens import make_tokens, most_frequent_tokens, make_tags
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
    
    # create tokens for the 100 first addresses
    tokens = make_tokens(adresse.sample(1000), remp_file)
    # frequent = most_frequent_tokens(tokens, 300)
    # print(tokens[0:500])
    # print(frequent)

    tags = make_tags(tokens, lib_voie)
    print(tags)