from standardization.tokenization import tokenize
from standardization.tagging import tag, df_tags, remove_perso_info
from utils.csv_io import import_csv, export_csv
from utils.sample import Sample
from HMM.transition import create_train_test_sample, compute_transition_matrix
import pandas as pd


if __name__ == '__main__':
    BUCKET = 'projet-pfe-adress-matching'
    FILE_KEY_S3 = 'DonneesCompletes.csv'

    # import of the data
    full_df = import_csv(BUCKET, FILE_KEY_S3)

    # sample
    sample = Sample(dataset=full_df, size=10000)
    sample_df = sample.create_sample()

    #  put the sample in the BUCKET (avoid to push it by mistake)
    sample.save_sample_file(BUCKET, 'sample.csv')

    # import others datasets
    df_sample = import_csv(BUCKET, 'sample.csv', sep=',')
    replacement = pd.read_csv('remplacement.csv', sep=",")
    lib_voie = pd.read_csv('libvoie.csv', sep=",")

    df = df_sample.iloc[:, :8]

    # extract addresses column
    adresse = df.iloc[:, 0]

    # create tokens for the 100 first addresses
    tokens = tokenize(adresse, replacement_file=replacement)

    # frequent = most_frequent_tokens(tokens, 100)
    # print(frequent)

    tags = tag(tokens, libvoie_file=lib_voie)

    tags_without_perso = remove_perso_info(tags)
    print(tags_without_perso[0:100])

    train_sample = create_train_test_sample(tags_without_perso)[0]

    # display_statistics(train_sample)
    transition_matrix = compute_transition_matrix(tags_without_perso)
    print(transition_matrix)

    df_train = df_tags(tags_without_perso)

    df_train.to_csv('train.csv', index=False)

    FILE_KEY_S3_TRAIN = "train.csv"
    export_csv(df_train, BUCKET, FILE_KEY_S3_TRAIN)
