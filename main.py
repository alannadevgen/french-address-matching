from standardization.tokenization import *
from standardization.tagging import *
from utils.csv_io import *
import pandas as pd
# from random.sample import *

if __name__ == '__main__':
    BUCKET = 'projet-pfe-adress-matching'
    FILE_KEY_S3 = 'sample.csv'

    # import the datasets
    df_complet = import_csv(BUCKET, FILE_KEY_S3, sep=',')
    replacement = pd.read_csv('remplacement.csv', sep=",")
    lib_voie = pd.read_csv('libvoie.csv', sep=",")

    df = df_complet.iloc[:, :8]

    # extract addresses column
    adresse = df.iloc[:, 0]

    # sample = adresse.sample(10000)
    # sample.to_csv("sample.csv")

    # create tokens for the 100 first addresses
    tokens = tokenize(adresse,replacement_file=replacement)
    
    # frequent = most_frequent_tokens(tokens, 100)
    # print(frequent)

    tags = tag(tokens, libvoie_file=lib_voie)

    # tags2 = remove_perso_info(tags)

    df = df_tags(tags)
    # df2 = df_tags(tags2)
    df.to_csv('train.csv', index=False)

    FILE_KEY_S3_TRAIN = "train.csv"
    export_csv(df, BUCKET, FILE_KEY_S3_TRAIN)

