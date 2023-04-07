from utils.file_io import FileIO


class IOpng(FileIO):
    def import_file(self):
        pass

    def export_file(self, image, bucket: str, file_key_s3: str):
        file_system = self.get_credentials()
        file_path_s3 = bucket + "/" + file_key_s3

        with file_system.open(file_path_s3, 'wb') as f:
            f.write(image.getbuffer())
