import s3fs
import json
import os


class IOjson:
    def get_credentials(self):
        '''
        Get the credentials to connect to the S3 Datalab file system
        '''
        # environment variables
        CLIENT_KWARGS = {
            'endpoint_url': 'https://' + os.environ['AWS_S3_ENDPOINT']
        }
        KEY = os.environ['AWS_ACCESS_KEY_ID']
        SECRET = os.environ['AWS_SECRET_ACCESS_KEY']
        TOKEN = os.environ['AWS_SESSION_TOKEN']
        file_system = s3fs.S3FileSystem(
            client_kwargs=CLIENT_KWARGS,
            key=KEY,
            secret=SECRET,
            token=TOKEN
        )
        return file_system

    def import_json(
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

    def export_json(self, dict_file, bucket: str, file_key_s3: str):
        '''
        export_json allow to transform a dictionnary into a csv file
        and to export it with any vscode service on the datalab using
        management of env variables
        '''
        file_system = self.get_credentials()
        file_path_s3 = bucket + "/" + file_key_s3

        with file_system.open(file_path_s3, 'w') as file_output:
            json.dump(dict_file, file_output)
