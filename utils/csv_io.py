import s3fs
import pandas as pd
import os


def import_csv(bucket, file_key_s3, encoding='utf8', sep=';'):
    '''
    import_csv allows to import csv file containing the addresses
    with any vscode service on the datalab thanks to management of
    environment variables
    returns a pandas dataframe
    '''
    # environment variables
    CLIENT_KWARGS = {'endpoint_url': 'https://' +
                     os.environ['AWS_S3_ENDPOINT']}
    KEY = os.environ['AWS_ACCESS_KEY_ID']
    SECRET = os.environ['AWS_SECRET_ACCESS_KEY']
    TOKEN = os.environ['AWS_SESSION_TOKEN']
    ###############

    fs = s3fs.S3FileSystem(
        client_kwargs=CLIENT_KWARGS,
        key=KEY,
        secret=SECRET,
        token=TOKEN
        )
    file_path_s3 = bucket + "/" + file_key_s3

    with fs.open(file_path_s3, mode="rb") as file_in:
        df = pd.read_csv(file_in, sep=sep, encoding=encoding)
    return df


def export_csv(df, bucket, file_key_s3):
    '''
    export_csv allow to transform a pandas dataframe into a csv file and to export it 
    with any vscode service on the datalab thanks to management of env variables
    '''
    # env variables
    CLIENT_KWARGS = {'endpoint_url': 'https://' + os.environ['AWS_S3_ENDPOINT']}
    KEY = os.environ['AWS_ACCESS_KEY_ID']
    SECRET = os.environ['AWS_SECRET_ACCESS_KEY']
    TOKEN = os.environ['AWS_SESSION_TOKEN']
    ###############

    fs = s3fs.S3FileSystem(client_kwargs = CLIENT_KWARGS, key = KEY, secret = SECRET, token = TOKEN)
    file_path_s3 = bucket + "/" + file_key_s3

    with fs.open(file_path_s3, 'w') as file_out:
        df.to_csv(file_out, index=False)
