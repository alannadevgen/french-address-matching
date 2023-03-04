from standardization.tokenization import tokenize
from standardization.tagging import *
from utils.csv_io import import_csv, export_csv
from utils.sample import Sample
from HMM.transition import compute_transition_matrix, plot_transition_matrix
# from HMM.transition import creckages : on télécharge les données, on installe les librairies qui ne sont pas presentes par défaut et on récupère les fichiers nécessairesate_train_test_sample, compute_transition_matrix
import click
import pandas as pd
import numpy as np
from time import time


@click.command()
@click.option(
    '--create-sample',
    default=False,
    help='Create a new sample of the dataset.',
    type=bool
)
@click.option(
    '--size',
    default=10000,
    help='Sample size.',
    type=int
)
def main(create_sample, size):
    start_time = time()
    BUCKET = 'projet-pfe-adress-matching'
    FILE_KEY_S3 = 'DonneesCompletes.csv'

    if create_sample:
        print("Creating new sample.\n")
        # import of the data
        full_df = import_csv(BUCKET, FILE_KEY_S3)
        # initialisate a sample
        sample = Sample(dataset=full_df, size=size)
        # create the sample
        sample.create_sample()
        #  put the sample in the BUCKET (avoid to push it by mistake)
        sample.save_sample_file(BUCKET, 'sample.csv')
    else:
        print("Importing previously created sample.\n")
        # import the previous sample
        df_sample = import_csv(BUCKET, 'sample.csv', sep=';')

    # import others datasets
    df_sample = import_csv(BUCKET, 'sample.csv', sep=';')
    replacement = pd.read_csv('remplacement.csv', sep=",")
    lib_voie = pd.read_csv('libvoie.csv', sep=",")

    df = df_sample.iloc[:, :5]

    # extract addresses column
    print(df.head(20))

    '''
    addresses = df.iloc[:, 0]
    cp = df.iloc[:, 1]
    communes = df.iloc[:, 2]


    # create tokens for the 100 first addresses
    tokens_addresses = tokenize(addresses, replacement_file=replacement)
    tokens_communes = tokenize(communes, replacement_file=replacement)
    # print(tokens_communes[0:10])

    # print frequent tokens
    # frequent = most_frequent_tokens(tokens, 100)
    # print(frequent)

    # tag the tokens with their label
    tags = tag_tokens(
        tokens_addresses,
        cp,
        tokens_communes,
        libvoie_file=lib_voie
        )

    # remove personal information
    tags_without_perso = remove_perso_info(tags)
    clean_tags = tags_without_perso['tagged_tokens']
    # print(tags_without_perso[0:10])

    # train_sample = create_train_test_sample(tags_without_perso)[0]

    # display_statistics(train_sample)
    # transition_matrix = compute_transition_matrix(tags_without_perso)
    # print(transition_matrix)
    # plot_transition_matrix(transition_matrix)

    # df_train = df_tags(clean_tags)
    reattached_tokens = reattach_tokens(clean_tags, tags_without_perso['kept_addresses'])
    # print(reattached_tokens[0:100], len(reattached_tokens))

    df_train = tags_to_df(reattached_tokens)
    print(df_train.head(50))

    FILE_KEY_S3_TRAIN = "train.csv"
    export_csv(df_train, BUCKET, FILE_KEY_S3_TRAIN)
    '''

    # retrieve tagged addresses
    tagged_addresses = import_csv(BUCKET, 'train.csv', sep=';')
    print(tagged_addresses.head())

    complete_df = tagged_addresses.set_index('INDEX').join(df)

    complete_df['cp'] = complete_df['cp'].replace(np.nan, 0)
    complete_df['cp'] = complete_df['cp'].astype(int)
    complete_df['cp'] = complete_df['cp'].astype(str)

    complete_df['index'] = list(complete_df.index)

    cols = list(complete_df.columns)

    for index, row in complete_df.iterrows():
        print(index, complete_df.iloc[index, cols.index('LIBVOIE')])

        if len(complete_df.iloc[index, cols.index('cp')]) == 4:
            complete_df.iloc[index, cols.index('cp')] = '0' +\
                complete_df.iloc[index, cols.index('cp')]

        if len(complete_df.iloc[index, cols.index('CODGEO_2021')]) == 4:
            complete_df.iloc[index, cols.index('CODGEO_2021')] = '0' +\
                complete_df.iloc[index, cols.index('CODGEO_2021')]


    print(complete_df.head(30))

    execution_time = time() - start_time
    print(f"Took {round(execution_time, 2)} seconds (approx. {round(execution_time/60)} minutes)")


if __name__ == '__main__':
    main()
