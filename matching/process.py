from matching.matching import match_addresses, match_addresses_cor,\
    incorrect_addresses, create_training_dataset_json,\
    create_training_dataset_csv
from utils.csv_io import IOcsv
from utils.json_io import IOjson
from standardization.tagging import remove_perso_info, reattach_tokens,\
    tags_to_df
from standardization.tokenization import tokenize_code


def process_matching(tags, df, postal_code_col, city_code_col,
                     add_corected_addresses, BUCKET, process='hc'):
    file_io_csv = IOcsv()
    file_io_json = IOjson()
    # remove personal information
    tags_without_perso = remove_perso_info(tags)
    clean_tags = tags_without_perso['tagged_tokens']

    # reattach tokens together to have standardized adresses
    reattached_tokens = reattach_tokens(
        clean_tags, tags_without_perso['kept_addresses'])

    tagged_addresses = tags_to_df(reattached_tokens)

    # stock indexes in a column
    # print('index', tagged_addresses['INDEX'])
    tagged_addresses['index'] = tagged_addresses['INDEX']
    # print(tagged_addresses.head())

    # merge tagged tokens (complete_df) with original data (df)
    # print(df)
    tagged_addresses['INDEX'] = [int(elem) for elem in tagged_addresses['INDEX']]
    complete_df = tagged_addresses.set_index('INDEX').join(df)
    # print(complete_df)

    complete_df.index = [ind for ind in range(complete_df.shape[0])]
    complete_df[postal_code_col] = tokenize_code(
        complete_df[postal_code_col]
        )
    # print(complete_df[postal_code_col])
    complete_df[city_code_col] = tokenize_code(complete_df[city_code_col])
    # print(complete_df.head())

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
    #####################################################################

    #####################################################################
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
                    matched_addresses['index'] == index_address
                    ].iloc[0, cols.index('label')])
            print('ADDRESS RETURNED BY THE API\
                (with previous corrections)\n',
                  matched_addresses[
                    matched_addresses['index'] == index_address
                    ].iloc[0, cols.index('label_corr')])
            print('\n')

    train_json = create_training_dataset_json(tags, matched_addresses,
                                              incorrect_indexes)
    FILE_KEY_S3_TRAIN_JSON = f"{process}.json"
    file_io_json.export_file(train_json, BUCKET, FILE_KEY_S3_TRAIN_JSON)

    train_csv = create_training_dataset_csv(tags, matched_addresses,
                                            incorrect_indexes)
    FILE_KEY_S3_TRAIN_CSV = f"{process}.csv"
    file_io_csv.export_file(train_csv, BUCKET, FILE_KEY_S3_TRAIN_CSV)
