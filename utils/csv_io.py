import pandas as pd
from utils.file_io import FileIO


class IOcsv(FileIO):
    def import_file(
        self, bucket: str, file_key_s3: str,
        encoding='utf8', sep=';'
    ):
        '''
        import_csv allows to import csv file containing the addresses
        with any vscode service on the datalab thanks to management of
        environment variables
        returns a pandas dataframe
        '''
        file_system = self.get_credentials()
        file_path_s3 = bucket + "/" + file_key_s3

        with file_system.open(file_path_s3, mode="rb") as file_input:
            df = pd.read_csv(file_input, sep=sep, encoding=encoding)
        return df

    def export_file(self, df, bucket: str, file_key_s3: str):
        '''
        export_csv allow to transform a pandas dataframe into a csv file
        and to export it with any vscode service on the datalab using
        management of env variables
        '''
        file_system = self.get_credentials()
        file_path_s3 = bucket + "/" + file_key_s3

        with file_system.open(file_path_s3, mode='w') as file_output:
            df.to_csv(file_output, index=False, sep=';')
