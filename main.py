from standardization.tokenization import tokenize
from standardization.tagging import tag_tokens, tags_to_df, reattach_tokens,\
    remove_perso_info
from matching.matching import match_addresses, match_addresses_cor,\
    incorrect_addresses
from utils.csv_io import IO
from utils.sample import Sample
import click
import pandas as pd
import numpy as np
from time import time
# from HMM.transition import compute_transition_matrix, plot_transition_matrix
# from HMM.transition import creckages :
# on télécharge les données, on installe les librairies qui ne sont pas
# presentes par défaut et on récupère les fichiers nécessairesate_train
# test_sample, compute_transition_matrix


@click.command()
@click.option(
    '--create-sample',
    default=False,
    help='Create a new sample of the dataset.',
    type=bool
)
@click.option(
    '--size',
    default=1000,
    help='Sample size.',
    type=int
)
def main(create_sample, size):
    start_time = time()
    BUCKET = 'projet-pfe-adress-matching'
    FILE_KEY_S3 = 'DonneesCompletes.csv'
    file_io = IO()

    if create_sample:
        print("Creating new sample.\n")
        # import of the data
        full_df = file_io.import_csv(BUCKET, FILE_KEY_S3)
        # initialisate a sample
        sample = Sample(dataset=full_df, size=size)
        # create the sample
        sample.create_sample()
        #  put the sample in the BUCKET
        sample.save_sample_file(BUCKET, 'sample.csv')
    else:
        print("Importing previously created sample.\n")
        # import the previous sample
        df_sample = file_io.import_csv(
            bucket=BUCKET, file_key_s3='sample.csv', sep=';'
        )

    # import others datasets
    df_sample = file_io.import_csv(BUCKET, 'sample.csv', sep=';')
    replacement = pd.read_csv('remplacement.csv', sep=",")
    lib_voie = pd.read_csv('libvoie.csv', sep=",")

    df = df_sample[['adresse', 'cp_corr', 'CODGEO_2021', 'adresse_corr',
                    'result_label']]

    # extract addresses column
    addresses = df.iloc[:, 0]
    cp = df.iloc[:, 1]
    communes = df.iloc[:, 2]

    # create tokens for the 100 first addresses
    tokens_addresses = tokenize(addresses, replacement_file=replacement)
    tokens_communes = tokenize(communes, replacement_file=replacement)

    # print frequent tokens
    # frequent = most_frequent_tokens(tokens, 100)
    # print(frequent)

    #################################
    # tag the tokens with their label
    tags = tag_tokens(
        tokens_addresses,
        cp,
        tokens_communes,
        libvoie_file=lib_voie
    )
    #################################

    #############################
    # remove personal information
    tags_without_perso = remove_perso_info(tags)
    clean_tags = tags_without_perso['tagged_tokens']
    #############################

    # train_sample = create_train_test_sample(tags_without_perso)[0]

    # display_statistics(train_sample)
    # transition_matrix = compute_transition_matrix(tags_without_perso)
    # print(transition_matrix)
    # plot_transition_matrix(transition_matrix)

    ########################################################
    # reattach tokens together to have standardized adresses
    reattached_tokens = reattach_tokens(
        clean_tags, tags_without_perso['kept_addresses'])

    df_train = tags_to_df(reattached_tokens)

    FILE_KEY_S3_TRAIN = "train.csv"
    file_io.export_csv(df_train, BUCKET, FILE_KEY_S3_TRAIN)
    ########################################################

    # import train.csv
    tagged_addresses = file_io.import_csv(bucket=BUCKET,
                                          file_key_s3='train.csv',
                                          sep=';')

    # keep indexes in a column
    tagged_addresses['index'] = tagged_addresses['INDEX']

    # merge tagged tokens (complete_df) with original data (df)
    complete_df = tagged_addresses.set_index('INDEX').join(df)

    # change indexes to iter over them
    complete_df.index = [ind for ind in range(complete_df.shape[0])]

    # correct format of postal code (float to str)
    complete_df['cp_corr'] = complete_df['cp_corr'].replace(np.nan, 0)
    complete_df['cp_corr'] = complete_df['cp_corr'].astype(int)
    complete_df['cp_corr'] = complete_df['cp_corr'].astype(str)

    # correct format of city code
    for index, row in complete_df.iterrows():
        try:
            complete_df.loc[index, 'CODGEO_2021'] = float(
                complete_df.loc[index, 'CODGEO_2021']
                )
            complete_df.loc[index, 'CODGEO_2021'] = int(
                complete_df.loc[index, 'CODGEO_2021']
                )
            complete_df.loc[index, 'CODGEO_2021'] = str(
                complete_df.loc[index, 'CODGEO_2021']
                )

        except:
            if complete_df.loc[index, 'CODGEO_2021'] == np.nan:
                complete_df.loc[index, 'CODGEO_2021'] = ''
            else:
                complete_df.loc[index, 'CODGEO_2021'] = str(
                    complete_df.loc[index, 'CODGEO_2021']
                    )

    # all columns
    cols = list(complete_df.columns)

    # correct format of postal code and city code (0 at the beginning)
    for index, row in complete_df.iterrows():

        if len(complete_df.iloc[index, cols.index('cp_corr')]) == 4:
            complete_df.iloc[index, cols.index('cp_corr')] = '0' +\
                complete_df.iloc[index, cols.index('cp_corr')]

        if len(complete_df.iloc[index, cols.index('CODGEO_2021')]) == 4:
            complete_df.iloc[index, cols.index('CODGEO_2021')] = '0' +\
                complete_df.iloc[index, cols.index('CODGEO_2021')]

    ##########################################
    # match the addresses with the API adresse
    matched_addresses = match_addresses(complete_df,
                                        numvoie_col='NUMVOIE',
                                        libvoie_col='LIBVOIE',
                                        lieu_col='LIEU',
                                        postal_code_col='cp_corr',
                                        city_code_col='CODGEO_2021')

    matched_corr_addresses = match_addresses_cor(matched_addresses,
                                                 'adresse_corr', 'CODGEO_2021',
                                                 'cp_corr')

    FILE_KEY_S3_MATCH = "matching.csv"
    file_io.export_csv(matched_corr_addresses, BUCKET, FILE_KEY_S3_MATCH)
    ##########################################

    #################
    # tags to correct
    incorrect_indexes = incorrect_addresses(matched_corr_addresses)
    print(len(incorrect_indexes))
    print(incorrect_indexes)

    # for index_address in incorrect_indexes:
    #     print(clean_tags[index_address])
    #################

    execution_time = time() - start_time
    seconds = round(execution_time, 2)
    minutes = round(execution_time/60)
    print(
        f"Took {seconds} seconds (approx. {minutes} minutes)"
    )


if __name__ == '__main__':
    main()
