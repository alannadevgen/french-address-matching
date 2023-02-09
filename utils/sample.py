from csv_io import import_csv, export_csv
import pandas as pd


class Sample:
    def __init__(self, dataset, size):
        self.dataset = pd.DataFrame(dataset)
        self.size = size

    def create_sample(self):
        self.sample_dataset = self.dataset.sample(
            n=self.size, replace=True, random_state=1
        )

    def save_sample_file(self, path, file):
        export_csv(self.sample_dataset, path, file)


if __name__ == "__main__":
    BUCKET = 'projet-pfe-adress-matching'
    FILE_KEY_S3 = 'DonneesCompletes.csv'

    # import of the data
    full_df = import_csv(BUCKET, FILE_KEY_S3)
    sample = Sample(dataset=full_df, size=10000)
    sample_df = sample.create_sample()
    # put the sample in the BUCKET (avoid to push it by mistake)
    sample.save_sample_file(BUCKET, 'sample.csv')
