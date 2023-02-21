from standardization.tokenization import tokenize
from standardization.tagging import tag_tokens, df_tags, remove_perso_info
from utils.csv_io import import_csv, export_csv
from utils.sample import Sample
from HMM.transition import create_train_test_sample, compute_transition_matrix
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
def main(create_sample):
    start_time = time()
    BUCKET = 'projet-pfe-adress-matching'
    FILE_KEY_S3 = 'DonneesCompletes.csv'

    if create_sample:
        print("Creating new sample.\n")
        # import of the data
        full_df = import_csv(BUCKET, FILE_KEY_S3)
        # initialisate a sample
        sample = Sample(dataset=full_df, size=10000)
        # create the sample
        sample.create_sample()
        #  put the sample in the BUCKET (avoid to push it by mistake)
        sample.save_sample_file(BUCKET, 'sample.csv')
    else:
        print("Importing previously created sample.\n")
        # import the previous sample
        df_sample = import_csv(BUCKET, 'sample.csv', sep=',')

    # import others datasets
    df_sample = import_csv(BUCKET, 'sample.csv', sep=',')
    replacement = pd.read_csv('remplacement.csv', sep=",")
    lib_voie = pd.read_csv('libvoie.csv', sep=",")

    df = df_sample.iloc[:, :8]

    # extract addresses column
    addresses = df.iloc[:, 0]

    # create tokens for the 100 first addresses
    tokens = tokenize(addresses, replacement_file=replacement)

    # print frequent tokens
    # frequent = most_frequent_tokens(tokens, 100)
    # print(frequent)

    # tag the tokens with their label
    tags = tag_tokens(tokens, libvoie_file=lib_voie)
    # remove personal information
    tags_without_perso = remove_perso_info(tags)
    print(tags_without_perso[0:100])


    # train_sample = create_train_test_sample(tags_without_perso)[0]

    # display_statistics(train_sample)
    # transition_matrix = compute_transition_matrix(tags_without_perso)
    # print(transition_matrix)

    # df_train = df_tags(tags_without_perso)

    # df_train.to_csv('train.csv', index=False)

    # FILE_KEY_S3_TRAIN = "train.csv"
    # export_csv(df_train, BUCKET, FILE_KEY_S3_TRAIN)

    adresse = [['ETAGE', '2', '1', 'A', 'RUE', 'DES', 'LILAS']]
    print(tag_tokens(adresse, lib_voie))

    execution_time = time() - start_time
    print(f"Took {round(execution_time, 2)} seconds (approx. {round(execution_time/60)} minutes)")


if __name__ == '__main__':
    main()
adresse = [['ETAGE', '2', '43', 'A', 'RUE', 'DES', 'LILAS']]
print(tag_tokens(adresse, lib_voie))