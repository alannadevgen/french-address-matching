from utils.file_io import FileIO
import pickle


class IOpkl(FileIO):
    def import_file(
        self, bucket: str, file_key_s3: str,
        encoding='utf8', sep=';'
    ):
        '''
        import_csv allows to import plk file containing the model
        '''
        file_system = self.get_credentials()
        file_path_s3 = bucket + "/" + file_key_s3

        with file_system.open(file_path_s3, mode="rb") as file_input:
            file_pkl = pickle.load(file_input)
        return file_pkl

    def export_file(self, file, bucket: str, file_key_s3: str, index=False):
        '''
        export_csv allow to export plk file containing the model
        '''
        file_system = self.get_credentials()
        file_path_s3 = bucket + "/" + file_key_s3

        with file_system.open(file_path_s3, mode='wb') as file_output:
            pickle.dump(file, file_output)
