import requests
import numpy as np
import pandas as pd


def match_address(numvoie=None, libvoie=None, lieudit=None, citycode=None,
                  postalcode=None, autocomplete=False):
    '''
    '''
    to_return = {}
    query = ''
    req_type = ''
    correct_query = True

    if numvoie:
        req_type = 'housenumber'
        query += str(numvoie) + ' '
    if libvoie:
        query += str(libvoie) + ' '
        if not numvoie:
            req_type = 'street'
    elif lieudit:
        query += str(lieudit)
        if not numvoie:
            req_type = 'municipality'
    else:
        correct_query = False

    if citycode:
        query += '&citycode=' + str(citycode)

    if postalcode:
        query += '&postalcode=' + str(postalcode)

    if correct_query:
        
        def_query = 'https://api-adresse.data.gouv.fr/search/?q=' +\
                     query +\
                     '&type=' + req_type +\
                     '&autocomplete=' + str(int(autocomplete))

        print(def_query)
            
        req = requests.get(def_query)

        if req.status_code == 200:
            res  = req.json()
            final = res['features']
            if final:
                to_return = final[0]['properties']
            else:
                to_return = {'error': 'not found'}
        # print(to_return)
        if not to_return:
            to_return = {'error': 'incorrect'}
    return to_return


# def match_addresses(df):
#     '''
#     '''
#     cols = list(df.columns)
#     cols_to_add = {}
#     elem_to_add = ['label', 'score']
#     for elem in elem_to_add:
#         cols_to_add[elem] = []
#     for index, row in df.iterrows():
#         numvoie = df.iloc[index, cols.index('NUMVOIE')]
#         libvoie = df.iloc[index, cols.index('LIBVOIE')]
#         lieu = df.iloc[index, cols.index('LIEU')]
#         postal_code = df.iloc[index, cols.index('cp')]
#         city_code = df.iloc[index, cols.index('CODGEO_2021')]

#         if pd.isna(numvoie):
#             numvoie = None
#         if pd.isna(libvoie):
#             libvoie = None
#         if pd.isna(lieu):
#             lieu = None
#         if libvoie and lieu:
#             lieu = None
#         if pd.isna(postal_code):
#             postal_code = None
#         if pd.isna(city_code):
#             city_code = None

#         res_match = match_address(numvoie=numvoie,
#                                   libvoie=libvoie,
#                                   lieudit=lieu,
#                                   citycode=city_code,
#                                   postalcode=postal_code)
        
#         if 'error' not in list(res_match.keys()):
#             for elem in elem_to_add:
#                 cols_to_add[elem].append(res_match[elem])
#         else:
#             for elem in elem_to_add:
#                 cols_to_add[elem].append(res_match['error'])
        
#     for elem in elem_to_add:
#         df[elem] = cols_to_add[elem]
    
#     return df
