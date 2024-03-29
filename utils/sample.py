from utils.csv_io import IOcsv
import pandas as pd


class Sample:
    def __init__(self, dataset, size):
        self.dataset = pd.DataFrame(dataset)
        self.size = size
        self.file_io = IOcsv()

    def create_sample(self):
        self.sample_dataset = self.dataset.sample(
            n=self.size, replace=False
        )

    def save_sample_file(self, path, file):
        self.file_io.export_file(self.sample_dataset, path, file)
