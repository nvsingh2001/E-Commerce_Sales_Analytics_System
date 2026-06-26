import os
import pandas as pd
from config.settings import Settings
from services.s3_service import S3Service


class DatasetDownloader:
    def __init__(self, s3_service=None):
        self.s3_service = s3_service or S3Service()
        self.xlsx_path = "data/raw/online_retail_II.xlsx"
        self.csv_path = Settings.LOCAL_RAW_PATH
        os.makedirs(os.path.dirname(self.xlsx_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

    def validate_dataset(self):
        print("Checking dataset...")
        if not os.path.exists(self.xlsx_path):
            raise FileNotFoundError(f"{self.xlsx_path} not found.")
        print("Dataset found.")

    def convert_to_csv(self):
        print("Converting XLSX to CSV...")
        df = pd.read_excel(self.xlsx_path, engine="openpyxl")
        df.to_csv(self.csv_path, index=False)
        print("CSV file created successfully.")

    def upload_to_s3(self):
        print("Uploading CSV to S3...")
        self.s3_service.upload_file(
            file_path=self.csv_path,
            bucket_name=Settings.S3_BUCKET,
            key="raw/online_retail_II.csv",
        )
        print("CSV uploaded successfully.")

    def run(self):
        self.validate_dataset()
        self.convert_to_csv()
        self.upload_to_s3()


if __name__ == "__main__":
    downloader = DatasetDownloader()
    downloader.run()