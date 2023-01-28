from standardization.tokens import make_tokens, most_frequent_tokens
from standardization.import_csv import import_csv

if __name__ == '__main__':
    BUCKET = 'projet-pfe-adress-matching'
    FILE_KEY_S3 = 'DonneesCompletes.csv'

    # import of the data
    df_complet = import_csv(BUCKET, FILE_KEY_S3)
    df = df_complet.iloc[:, :8]

    # extract addresses column
    adresse = df.iloc[:, 0]
    
    # create tokens for the 100 first addresses
    tokens = make_tokens(adresse[0:1000000])
    # frequent = most_frequent_tokens(tokens, 300)
    print(tokens[0:500])
    # print(frequent)