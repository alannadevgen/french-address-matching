from standardization.tokenization import tokenize_label, tokenize_code
from standardization.tagging import tag_tokens, tags_to_df, reattach_tokens,\
    remove_perso_info
from matching.matching import match_addresses, match_addresses_cor,\
    incorrect_addresses, create_training_dataset_json,\
    create_training_dataset_csv
from utils.csv_io import IOcsv
from utils.json_io import IOjson
from utils.sample import Sample
import click
import pandas as pd
from time import time
from HMM.transition_matrix import TransitionMatrix
from HMM.emission import Emission
from HMM.viterbi import Viterbi
from HMM.split_sample import SplitSample
from HMM.performance import Performance

@click.command()
@click.argument(
    'bucket',
    type=str
)
@click.argument(
    'csv_file',
    type=str
)
@click.argument(
    'addresses_col',
    type=str
)
@click.argument(
    'cities_col',
    type=str
)
@click.argument(
    'postal_code_col',
    type=str
)
@click.argument(
    'city_code_col',
    type=str
)
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
@click.option(
    '--correct_addresses',
    default='adresse_corr',
    help='Column containing corrected addresses.',
    type=str
)
# PERFORM ONLY HMM AND DO NOT BUILD A TRAINING DATASET
# (by default --steps is hmm)
@click.option(
    '--steps',
    default='hmm',
    help='Steps to perform : "train", "hmm", "all"',
    type=str
)
def main(bucket, csv_file, addresses_col, cities_col, postal_code_col,
         city_code_col, create_sample, size, correct_addresses, steps):

    # Summary of the parameters given by the user
    print(f'Loading data from bucket: {bucket}')
    print(f'Using the following csv file: {csv_file}')
    print(f'Addresses column: {addresses_col}')
    print(f'Cities column: {cities_col}')
    print(f'Postal code column given: {postal_code_col}')
    print(f'City code column (INSEE code) given: {city_code_col}', '\n')

    start_time = time()
    BUCKET = bucket
    FILE_KEY_S3 = csv_file
    file_io_csv = IOcsv()
    file_io_json = IOjson()

    if steps in ['all', 'train']:

        if create_sample:
            print("Creating new sample.\n")
            # import of the data
            full_df = file_io_csv.import_file(BUCKET, FILE_KEY_S3)
            # initialisate a sample
            sample = Sample(dataset=full_df, size=size)
            # create the sample
            sample.create_sample()
            #  put the sample in the BUCKET
            sample.save_sample_file(BUCKET, 'sample.csv')
        else:
            print("Importing previously created sample.\n")
            # import the previous sample
            df_sample = file_io_csv.import_file(
                bucket=BUCKET, file_key_s3='sample.csv', sep=';'
            )

        #########################################################################
        # import csv file
        df_sample = file_io_csv.import_file(BUCKET, 'final_sample.csv', sep=';')

        # import other datasets (contained in the project)
        replacement = pd.read_csv('remplacement.csv', sep=",")
        lib_voie = pd.read_csv('libvoie.csv', sep=",")

        add_corected_addresses = True
        if correct_addresses in df_sample.columns:
            df = df_sample[[addresses_col, postal_code_col, cities_col,
                            city_code_col, correct_addresses]]
        else:
            df = df_sample[[addresses_col, postal_code_col, cities_col,
                            city_code_col]]
            add_corected_addresses = False

        # extract different columns to transform them
        addresses = df[addresses_col]
        cp = df[postal_code_col]
        communes = df[cities_col]

        # create tokens for the 100 first addresses
        tokens_addresses = tokenize_label(addresses, replacement_file=replacement)
        tokens_communes = tokenize_label(communes, replacement_file=replacement)
        clean_cp = tokenize_code(cp)

        # tag the tokens with their label
        tags = tag_tokens(
            tokens_addresses,
            clean_cp,
            tokens_communes,
            libvoie_file=lib_voie
        )

        # remove personal information
        tags_without_perso = remove_perso_info(tags)
        clean_tags = tags_without_perso['tagged_tokens']

        # reattach tokens together to have standardized adresses
        reattached_tokens = reattach_tokens(
            clean_tags, tags_without_perso['kept_addresses'])

        df_train = tags_to_df(reattached_tokens)

        FILE_KEY_S3_REATTACHED = "reattached_tokens.csv"
        file_io_csv.export_file(df_train, BUCKET, FILE_KEY_S3_REATTACHED)

        #########################################################################

        #########################################################################
        # import the previous file
        tagged_addresses = file_io_csv.import_file(bucket=BUCKET,
                                                   file_key_s3='reattached_tokens.csv',
                                                   sep=';')

        # keep indexes in a column
        tagged_addresses['index'] = tagged_addresses['INDEX']

        # merge tagged tokens (complete_df) with original data (df)
        complete_df = tagged_addresses.set_index('INDEX').join(df)

        complete_df.index = [ind for ind in range(complete_df.shape[0])]
        complete_df[postal_code_col] = tokenize_code(complete_df[postal_code_col])
        complete_df[city_code_col] = tokenize_code(complete_df[city_code_col])

        # change indexes to iter over them
        complete_df.index = [ind for ind in range(complete_df.shape[0])]

        # match the addresses with the API adresse
        matched_addresses = match_addresses(complete_df,
                                            numvoie_col='NUMVOIE',
                                            libvoie_col='LIBVOIE',
                                            lieu_col='LIEU',
                                            postal_code_col=postal_code_col,
                                            city_code_col=city_code_col)

        # add corr_addresses
        if add_corected_addresses:
            matched_addresses = match_addresses_cor(matched_addresses,
                                                    'adresse_corr',
                                                    city_code_col,
                                                    postal_code_col)

        FILE_KEY_S3_MATCH = "matching.csv"
        file_io_csv.export_file(matched_addresses, BUCKET, FILE_KEY_S3_MATCH)
        #########################################################################

        #########################################################################
        matched_addresses = file_io_csv.import_file(BUCKET,
                                                    'matching.csv', sep=';')
        incorrect_indexes = None
        if add_corected_addresses:
            incorrect_indexes = incorrect_addresses(matched_addresses)
            print(f'NUMBER OF ADDRESSES WITH POSSIBLE '
                f'INCORRECT TAGS: {len(incorrect_indexes)}\n')
            print('INDEXES OF THESE ADDRESSES:')
            print(incorrect_indexes, '\n')

            cols = list(matched_addresses.columns)
            for index_address in incorrect_indexes:
                print(f'INDEX {index_address}\n')
                print('TAGGING\n', tags[index_address])
                print('ADDRESS RETURNED BY THE API (with our tags)\n',
                    matched_addresses[
                        matched_addresses['index'] ==
                        index_address].iloc[0, cols.index('label')
                                            ])
                print('ADDRESS RETURNED BY THE API (with previous corrections)\n',
                    matched_addresses[
                        matched_addresses['index'] ==
                        index_address].iloc[0, cols.index('label_corr')
                                            ])
                print('\n')

        train_json = create_training_dataset_json(tags, matched_addresses,
                                                incorrect_indexes)
        FILE_KEY_S3_TRAIN_JSON = "train.json"
        file_io_json.export_file(train_json, BUCKET, FILE_KEY_S3_TRAIN_JSON)

        train_csv = create_training_dataset_csv(tags, matched_addresses,
                                                incorrect_indexes)
        FILE_KEY_S3_TRAIN_CSV = "train.csv"
        file_io_csv.export_file(train_csv, BUCKET, FILE_KEY_S3_TRAIN_CSV)

        train_non_valid = train_csv[train_csv['valid'] == False]
        file_io_csv.export_file(train_non_valid, BUCKET, 'non_valid.csv')

    #########################################################################
    if steps in ['all', 'hmm']:
        FILE_KEY_S3_TRAIN_JSON = "final_train.json"

        # list of possible incorrect addresses
        add_corected_addresses = True
        addresses_to_check = []
        list_addresses = file_io_json.import_file(BUCKET,
                                                  FILE_KEY_S3_TRAIN_JSON)
        all_tokens = []
        all_tags = []

        # stock indexes to be sure that we do not put an address twice !
        recorded_indexes = []
        for adress in list(list_addresses.keys()):
            if list_addresses[adress]['index_input'] not in recorded_indexes:
                recorded_indexes.append(list_addresses[adress]['index_input'])
                complete_adress = list_addresses[adress]
                if add_corected_addresses and not complete_adress['valid']:
                    addresses_to_check.append(complete_adress)
                else:
                    all_tokens.append(complete_adress['tokens'])
                    all_tags.append(complete_adress['tags'])

        # list of all tokens and tags for one address
        list_all_tags = list(zip(
            all_tokens, all_tags
                ))

        # statistics
        print("Number of addresses to check:", len(addresses_to_check))
        print("Number of addresses in the final training dataset:",
              len(list_all_tags))
        # 9796
        # 10,000 addresses and 9,985 addresses
        # (remove addresses containing PERSO)
        # 189 non valid addresses -> 9,985 - 189 = 9796 -> ok !

        # tags of the final (sample)
        tm = TransitionMatrix()

        transition_matrix = tm.compute_transition_matrix(list_all_tags)
        print("\n----------------------------------------------------------------------------------------------------------------\n")
        print("Transition matrix\n\n", transition_matrix)
        image = tm.plot_transition_matrix(transition_matrix)
        tm.save_transition_matrix(image=image, bucket=BUCKET)

        sp = SplitSample(list_all_tags)
        train_data, test_data = sp.split()
        viterbi = Viterbi(train_data)
        predictions = viterbi.predict(test_data)
        perf = Performance(test_data, predictions)
        good_class, bad_class = perf.rate_correct_tagged()
        print(f'Proportion of addresses correctly tagged:{good_class}')
        print(f'Proportion of addresses incorrectly tagged:{bad_class}')
        matrix = perf.matrix_true_pred()
        print(matrix)


    '''
    # CODE TRANSITION MATRIX WITH PERSO
    # tags of the final (sample)
    tm = TransitionMatrix()
    # tm.display_statistics(train_sample)
    transition_matrix = tm.compute_transition_matrix(tags)
    print("\n----------------------------------------------------------------------------------------------------------------\n")
    print("Transition matrix\n\n", transition_matrix)
    image = tm.plot_transition_matrix(transition_matrix)
    tm.save_transition_matrix(image=image, bucket=BUCKET)
    '''
    #################

    execution_time = time() - start_time
    seconds = round(execution_time, 2)
    minutes = round(execution_time/60)
    print(
        f"Took {seconds} seconds (approx. {minutes} minutes)"
    )


if __name__ == '__main__':
    main()
