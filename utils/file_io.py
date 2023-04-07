from abc import ABC, abstractmethod
import s3fs
import os


class FileIO(ABC):
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

    @abstractmethod
    def import_file(self):
        pass

    @abstractmethod
    def export_file(self):
        pass
