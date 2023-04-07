import json
from utils.file_io import FileIO


class IOjson(FileIO):
    def import_file(
        self, bucket: str, file_key_s3: str,
    ):
        '''
        import_json allows to import json file containing the addresses
        with any vscode service on the datalab thanks to management of
        environment variables
        returns a json
        '''
        file_system = self.get_credentials()
        file_path_s3 = bucket + "/" + file_key_s3

        with file_system.open(file_path_s3, mode="r") as file_input:
            dict_file = json.load(file_input)
        return dict_file

    def export_file(self, dict_file, bucket: str, file_key_s3: str):
        '''
        export_json allow to transform a dictionnary into a csv file
        and to export it with any vscode service on the datalab using
        management of env variables
        '''
        file_system = self.get_credentials()
        file_path_s3 = bucket + "/" + file_key_s3

        with file_system.open(file_path_s3, 'w') as file_output:
            json.dump(dict_file, file_output)
