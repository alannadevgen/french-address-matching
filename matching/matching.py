import requests
import pandas as pd


def match_address(numvoie=None, libvoie=None, lieudit=None, citycode=None,
                  postalcode=None, autocomplete=False, give_querytype=False):
    '''
    match_address: match an address with the API address and return the result
    of the query if there is one
    if the query is incorrect or does not have any result, return error
    '''
    query_result = {}
    query = ''
    querytype = ''
    correct_query = True

    if numvoie:
        querytype = 'housenumber'
        query += str(numvoie) + ' '
    if libvoie:
        query += str(libvoie) + ' '
        if not numvoie:
            querytype = 'street'
    elif lieudit:
        query += str(lieudit)
        if not numvoie:
            querytype = 'municipality'
    else:
        correct_query = False

    if citycode:
        query += '&citycode=' + str(citycode)

    if postalcode:
        query += '&postalcode=' + str(postalcode)

    if give_querytype:
        query += '&type=' + querytype

    if correct_query:
        def_query = 'https://api-adresse.data.gouv.fr/search/?q=' +\
                     query +\
                     '&autocomplete=' + str(int(autocomplete))

        req = requests.get(def_query)

        if req.status_code == 200:
            res = req.json()
            features = res['features']
            if features:
                query_result = features[0]['properties']
            else:
                query_result = {'error': 'not found'}
        else:
            print(f'Status code {req.status_code}')
            print(def_query)

    if not query_result and not correct_query:
        query_result = {'error': 'incorrect'}
    elif not query_result:
        query_result = {'error': 'no results'}

    return query_result


def match_addresses(df, numvoie_col, libvoie_col, lieu_col,
                    postal_code_col, city_code_col):
    '''
    match_addresses: match all the addresses of a dataframe with
    the API adresse
    '''
    cols = list(df.columns)
    cols_to_add = {}
    elem_to_add = ['id', 'label', 'score', 'postcode', 'citycode',
                   'city', 'type', 'x', 'y']
    for elem in elem_to_add:
        cols_to_add[elem] = []
    for index, row in df.iterrows():
        numvoie = df.iloc[index, cols.index(numvoie_col)]
        libvoie = df.iloc[index, cols.index(libvoie_col)]
        lieu = df.iloc[index, cols.index(lieu_col)]
        postal_code = df.iloc[index, cols.index(postal_code_col)]
        city_code = df.iloc[index, cols.index(city_code_col)]

        if pd.isna(numvoie):
            numvoie = None
        if pd.isna(libvoie):
            libvoie = None
        if pd.isna(lieu):
            lieu = None
        if libvoie and lieu:
            lieu = None
        if pd.isna(postal_code):
            postal_code = None
        if pd.isna(city_code):
            city_code = None

        res_match = match_address(numvoie=numvoie,
                                  libvoie=libvoie,
                                  lieudit=lieu,
                                  citycode=city_code,
                                  postalcode=postal_code)

        if 'error' not in list(res_match.keys()):
            for elem in elem_to_add:
                cols_to_add[elem].append(res_match[elem])
        else:
            for elem in elem_to_add:
                cols_to_add[elem].append(res_match['error'])

    for elem in elem_to_add:
        df[elem] = cols_to_add[elem]

    return df


def match_addresses_cor(df, addresses_corr_col, citycode_col, postalcode_col):
    '''
    add information returned by the API using previous correction
    '''
    cols = list(df.columns)
    cols_to_add = {}
    elem_to_add = ['id', 'label', 'score', 'postcode', 'citycode',
                   'city', 'type', 'x', 'y']

    for elem in elem_to_add:
        cols_to_add[elem] = []

    for index, row in df.iterrows():
        libvoie = df.iloc[index, cols.index(addresses_corr_col)]
        postal_code = df.iloc[index, cols.index(postalcode_col)]
        city_code = df.iloc[index, cols.index(citycode_col)]

        if pd.isna(libvoie):
            libvoie = None
        if pd.isna(postal_code):
            postal_code = None
        if pd.isna(city_code):
            city_code = None

        res_match = match_address(libvoie=libvoie,
                                  citycode=city_code,
                                  postalcode=postal_code)

        if 'error' not in list(res_match.keys()):
            for elem in elem_to_add:
                cols_to_add[elem].append(res_match[elem])
        else:
            for elem in elem_to_add:
                cols_to_add[elem].append(res_match['error'])

    for elem in elem_to_add:
        df[elem + '_corr'] = cols_to_add[elem]

    return df


def incorrect_addresses(df):
    '''
    return list of addresses considered incorrects
    '''
    cols = list(df.columns)
    count_indexes = df['index'].value_counts()
    addresses_to_correct = []
    for index, row in df.iterrows():
        if df.iloc[index, cols.index('id_corr')] not in\
            ['not found', 'no results', 'incorrect'] and\
            df.iloc[index, cols.index('id')] !=\
                df.iloc[index, cols.index('id_corr')] and\
                count_indexes[df.iloc[index, cols.index('index')]] == 1:
            addresses_to_correct.append(df.iloc[index, cols.index('index')])
    return addresses_to_correct


def create_training_dataset_json(list_tags, df_matching,
                                 index_incorrect_addresses=None, indexes=None):
    '''
    create the final json file of standardised addresses
    '''
    training_dataset = {}
    for index_tag in range(df_matching.shape[0]):
        training_dataset[index_tag] = {}

        index = df_matching.loc[index_tag, 'index']
        if indexes:
            index = int(indexes[index])
        tokens = list_tags[index][0]
        tags = list_tags[index][1]
        score = df_matching.loc[index_tag, 'score']
        score_corr = df_matching.loc[index_tag, 'score_corr']
        label = df_matching.loc[index_tag, 'label']
        label_corr = df_matching.loc[index_tag, 'label_corr']
        method = df_matching.loc[index_tag, 'method']
        valid = True
        if index_incorrect_addresses and\
                index in index_incorrect_addresses:
            valid = False
        training_dataset[index_tag]['index_input'] = str(index)
        training_dataset[index_tag]['tokens'] = tokens
        training_dataset[index_tag]['tags'] = tags
        training_dataset[index_tag]['valid'] = valid
        training_dataset[index_tag]['score'] = score
        training_dataset[index_tag]['score_corr'] = score_corr
        training_dataset[index_tag]['label'] = label
        training_dataset[index_tag]['label_corr'] = label_corr
        training_dataset[index_tag]['method'] = method
    return training_dataset


def create_training_dataset_csv(list_tags, df_matching,
                                index_incorrect_addresses=None, indexes=None):
    '''
    create the final csv file of standardised addresses
    '''
    training_dataset = pd.DataFrame()
    all_indexes = []
    all_tokens = []
    all_tags = []
    all_valid = []
    all_scores = []
    all_scores_corr = []
    all_labels = []
    all_labels_corr = []
    all_methods = []
    for index_tag in range(df_matching.shape[0]):
        index = df_matching.loc[index_tag, 'index']
        if indexes:
            index = int(indexes[index])
        tokens = list_tags[index][0]
        tags = list_tags[index][1]
        score = df_matching.loc[index_tag, 'score']
        score_corr = df_matching.loc[index_tag, 'score_corr']
        label = df_matching.loc[index_tag, 'label']
        label_corr = df_matching.loc[index_tag, 'label_corr']
        method = df_matching.loc[index_tag, 'method']
        valid = True
        if index_incorrect_addresses and\
                index in index_incorrect_addresses:
            valid = False
        all_indexes.append(index)
        all_tokens.append(tokens)
        all_tags.append(tags)
        all_valid.append(valid)
        all_scores.append(score)
        all_scores_corr.append(score_corr)
        all_labels.append(label)
        all_labels_corr.append(label_corr)
        all_methods.append(method)

    training_dataset['index_input'] = all_indexes
    training_dataset['tokens'] = all_tokens
    training_dataset['tags'] = all_tags
    training_dataset['valid'] = all_valid
    training_dataset['score'] = all_scores
    training_dataset['score_corr'] = all_scores_corr
    training_dataset['label'] = all_labels
    training_dataset['label_corr'] = all_labels_corr
    training_dataset['method'] = all_methods

    return training_dataset
