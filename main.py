from standardization.tokenization import tokenize
from standardization.tagging import tag_tokens, df_tags, remove_perso_info, df_tags2
from utils.csv_io import import_csv, export_csv
from utils.sample import Sample
from HMM.transition import compute_transition_matrix, plot_transition_matrix
# from HMM.transition import creckages : on télécharge les données, on installe les librairies qui ne sont pas presentes par défaut et on récupère les fichiers nécessairesate_train_test_sample, compute_transition_matrix
import click
import pandas as pd
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
    default=100,
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

    df = df_sample.iloc[:, :8]

    # extract addresses column
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
    res = df_tags2(clean_tags, tags_without_perso['kept_addresses'])
    print(res[0:100], len(res))

    # FILE_KEY_S3_TRAIN = "train.csv"
    # export_csv(df_train, BUCKET, FILE_KEY_S3_TRAIN)

    execution_time = time() - start_time
    print(f"Took {round(execution_time, 2)} seconds (approx. {round(execution_time/60)} minutes)")


if __name__ == '__main__':
    main()
