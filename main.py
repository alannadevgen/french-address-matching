from standardization.tokenization import tokenize_label, tokenize_code
from standardization.tagging import tag_tokens, tags_to_df, reattach_tokens,\
    remove_perso_info
from matching.matching import match_addresses, match_addresses_cor,\
    incorrect_addresses, create_training_dataset_json,\
    create_training_dataset_csv
from matching.process import process_matching
from utils.csv_io import IOcsv
from utils.json_io import IOjson
from utils.sample import Sample
import click
import pandas as pd
from time import time
from HMM.transition_matrix import TransitionMatrix
# from HMM.emission import Emission
from HMM.viterbi import Viterbi
from HMM.split_sample import SplitSample
from HMM.performance import Performance
# from HMM.emission import Emission
# from HMM.cross_validation import CrossValidation


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
    '--size',
    default=1000,
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
    help='Steps to perform : "create_sample", "hc", "hmm", "auto"',
    type=str
)
def main(bucket, csv_file, addresses_col, cities_col, postal_code_col,
         city_code_col, size, correct_addresses, steps, seuil_auto = 0.4):

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

    if steps == 'create_sample':
        print("Creating a sample.\n")
        # import of the data
        full_df = file_io_csv.import_file(BUCKET, FILE_KEY_S3)
        # initialisate a sample
        sample = Sample(dataset=full_df, size=size)
        # create the sample
        sample.create_sample()
        #  put the sample in the BUCKET
        sample.save_sample_file(BUCKET, 'sample.csv')
        df_sample = file_io_csv.import_file(
            bucket=BUCKET, file_key_s3='sample.csv', sep=';'
        )
    else:
        print("Importing all the dataset.\n")
        # import of the previous sample
        df_sample = file_io_csv.import_file(
            bucket=BUCKET, file_key_s3=FILE_KEY_S3, sep=';'
        )


    #####################################################################

    if steps in ['auto', 'hc', 'hmm']:
        # tokenization of the addresses:
        ################################

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

        # create tokens for addresses
        tokens_addresses = tokenize_label(addresses,
                                          replacement_file=replacement)
        ################################

        if steps in ['auto', 'hc']:
            # tagging with hcc:
            ################################
            tokens_communes = tokenize_label(communes,
                                             replacement_file=replacement)
            clean_cp = tokenize_code(cp)

            # tag the tokens with their label
            tags = tag_tokens(
                tokens_addresses,
                clean_cp,
                tokens_communes,
                libvoie_file=lib_voie
            )

            process_matching(tags, df, postal_code_col, city_code_col,
                             add_corected_addresses, BUCKET, process=steps)
            ################################

    #########################################################################
    if steps in ['auto', 'hmm']:

        # tagging with hmm (if hcc not done before)
        if steps == 'auto':
            FILE_KEY_S3_TRAIN_JSON = "auto.json"

        # SAMPLE with Marlène corr.
        ############################
        # list of possible incorrect addresses
        add_corected_addresses = True
        addresses_to_check = []
        list_addresses = file_io_json.import_file(BUCKET,
                                                  "final_train.json")
        # index considered valid by MK
        valid_MK = file_io_csv.import_file(BUCKET, 'valid_MK.csv')
        list_valid_MK = list((valid_MK['valid_MK']))

        all_tokens = []
        all_tags = []

        # stock indexes to be sure that we do not put an address twice !
        recorded_indexes = []
        for adress in list(list_addresses.keys()):
            if list_addresses[adress]['index_input'] not in recorded_indexes:
                recorded_indexes.append(list_addresses[adress]['index_input'])
                complete_adress = list_addresses[adress]
                if add_corected_addresses and not complete_adress['valid'] and\
                        int(complete_adress['index_input']) not\
                        in list_valid_MK:
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
        print("Number of addresses in the final training dataset " +
              "(containing only correct addresses):",
              len(list_all_tags))

        # tags of the final (sample)
        tm = TransitionMatrix()

        transition_matrix = tm.compute_transition_matrix(list_all_tags)
        print("\n----------------------------------------------------------------------------------------------------------------\n")
        print("Transition matrix (all addresses)\n\n", transition_matrix)
        image = tm.plot_transition_matrix(transition_matrix)
        tm.save_transition_matrix(
            image=image,
            bucket=BUCKET,
            file='hmm_results/transition_without_perso.png'
            )

        viterbi = Viterbi(list_all_tags)

        # tagging with hmm to improve hcc:
        #################################
        if steps == 'hmm':
            test_data = list(zip(tokens_addresses))
            predictions = viterbi.predict(test_data, delta=0.5)
            res_pred = list(zip(tokens_addresses, predictions))
            process_matching(res_pred, df, postal_code_col, city_code_col,
                             add_corected_addresses, BUCKET, process='hmm')

        else:
            test_data = file_io_json.import_file(BUCKET,
                                                 FILE_KEY_S3_TRAIN_JSON)
            list_tokens = []
            list_tags = []
            distinct_indexes = []
            for adr in list(test_data.keys()):
                if test_data[adr]['index_input'] not in distinct_indexes:
                    distinct_indexes.append(test_data[adr]['index_input'])
                    list_tokens.append(test_data[adr]['tokens'])
                    if not test_data[adr]['valid'] or\
                        test_data[adr]['score'].isdigit() and\
                            float(test_data[adr]['score']) < seuil_auto:
                        # (1)
                        obs_sequence = test_data[adr]['tokens']
                        pred_tags = viterbi.solve_viterbi(obs_sequence)
                        test_data[adr]['tags'] = pred_tags
                    list_tags.append(test_data[adr]['tags'])
            res_pred = list(zip(list_tokens, list_tags))
            # PB avec la ligne ci-dessous:
            #############################
            # décalage dans les indexs des addresses
            # mieux de modifier appariement avec API seulement sur les adresses
            # à corriger avec HMM condition (1) dans le code
            process_matching(res_pred, df, postal_code_col, city_code_col,
                             add_corected_addresses, BUCKET, process='auto')
    #########################################################################

    execution_time = time() - start_time
    seconds = round(execution_time, 2)
    minutes = round(execution_time/60)
    print(
        f"Took {seconds} seconds (approx. {minutes} minutes)"
    )


if __name__ == '__main__':
    main()
