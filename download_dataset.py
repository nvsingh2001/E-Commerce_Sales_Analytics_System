import os
import sys
import requests
import pandas as pd
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatasetIngestor:
    """
    Service class responsible for the Ingestion Stage:
    1. Downloads raw online retail dataset from public source URL.
    2. Reads and merges Excel sheets (multiple years).
    3. Saves merged data to a flat CSV.
    4. Uploads CSV to AWS S3 raw zone bucket.
    """
    def __init__(self, 
                 dataset_url: str = None, 
                 raw_dir: str = "datasets/raw",
                 excel_filename: str = "online_retail_II.xlsx",
                 csv_filename: str = "online_retail_II.csv"):
        
        self._dataset_url = dataset_url or "https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx"
        self._raw_dir = raw_dir
        self._excel_path = os.path.join(self._raw_dir, excel_filename)
        self._csv_path = os.path.join(self._raw_dir, csv_filename)
        
        self._s3_bucket = os.getenv("S3_BUCKET_NAME") or os.getenv("S3_BUCKET")
        self._aws_region = os.getenv("AWS_REGION", "ap-south-1")
        
        # Ensure directories exist
        os.makedirs(self._raw_dir, exist_ok=True)

    def download_raw_dataset(self) -> bool:
        """Downloads the dataset file if not already present locally."""
        if os.path.exists(self._excel_path):
            print(f"Local raw Excel dataset found at {self._excel_path}")
            return True
            
        print(f"Downloading dataset from: {self._dataset_url} (this may take a moment, ~45MB)...")
        try:
            response = requests.get(self._dataset_url, stream=True, timeout=30)
            response.raise_for_status()
            with open(self._excel_path, "wb") as f:
                total_length = int(response.headers.get("content-length", 0))
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_length > 0:
                            done = int(50 * downloaded / total_length)
                            print(
                                f"\rProgress: [{'=' * done}{' ' * (50 - done)}] {downloaded / (1024 * 1024):.2f}MB / {total_length / (1024 * 1024):.2f}MB",
                                end="",
                            )
            print("\nDownload complete.")
            return True
        except Exception as e:
            print(f"\nFailed to download dataset: {e}")
            return False

    def merge_excel_sheets_to_csv(self) -> bool:
        """Merges multiple year sheets from Excel workbook and saves to CSV."""
        if os.path.exists(self._csv_path):
            print(f"Local merged CSV dataset already exists at {self._csv_path}")
            return True
            
        print("Reading and merging Excel sheets (Year 2009-2010 and Year 2010-2011)...")
        try:
            xls = pd.ExcelFile(self._excel_path)
            print(f"Excel Sheet Names: {xls.sheet_names}")
            
            print("Reading Sheet 1: Year 2009-2010...")
            df1 = pd.read_excel(xls, "Year 2009-2010")
            print(f"Sheet 1 Rows: {len(df1)}")
            
            print("Reading Sheet 2: Year 2010-2011...")
            df2 = pd.read_excel(xls, "Year 2010-2011")
            print(f"Sheet 2 Rows: {len(df2)}")
            
            print("Merging datasets...")
            combined_df = pd.concat([df1, df2], ignore_index=True)
            print(f"Combined Total Rows: {len(combined_df)}")
            
            print(f"Saving merged dataset to CSV: {self._csv_path}...")
            combined_df.to_csv(self._csv_path, index=False)
            print("CSV conversion complete.")
            return True
        except Exception as e:
            print(f"Failed to merge Excel sheets and convert to CSV: {e}")
            return False

    def upload_csv_to_s3(self) -> bool:
        """Uploads local combined CSV dataset to S3 Raw bucket zone."""
        if not self._s3_bucket:
            print("Warning: S3_BUCKET_NAME not set in environment. Skipping upload.")
            return True
            
        print(f"Uploading raw CSV to Amazon S3 bucket '{self._s3_bucket}'...")
        try:
            s3_client = boto3.client("s3", region_name=self._aws_region)
            s3_key = "raw/online_retail_II.csv"
            
            file_size = os.path.getsize(self._csv_path)
            uploaded_bytes = 0
            
            def upload_progress(bytes_transferred):
                nonlocal uploaded_bytes
                uploaded_bytes += bytes_transferred
                done = int(50 * uploaded_bytes / file_size)
                print(
                    f"\rS3 Upload Progress: [{'=' * done}{' ' * (50 - done)}] {uploaded_bytes / (1024 * 1024):.2f}MB / {file_size / (1024 * 1024):.2f}MB",
                    end="",
                )
                
            s3_client.upload_file(
                Filename=self._csv_path, Bucket=self._s3_bucket, Key=s3_key, Callback=upload_progress
            )
            print(f"\nSuccessfully uploaded to S3: s3://{self._s3_bucket}/{s3_key}")
            return True
        except Exception as e:
            print(f"\nFailed to upload raw CSV to S3: {e}")
            return False

    def run(self) -> None:
        """Runs the complete ingestion pipeline lifecycle."""
        print("Initializing Dataset Ingestion Stage...")
        if not self.download_raw_dataset():
            sys.exit(1)
        if not self.merge_excel_sheets_to_csv():
            sys.exit(1)
        if not self.upload_csv_to_s3():
            sys.exit(1)
        print("Ingestion Stage completed successfully!")


def main():
    ingestor = DatasetIngestor()
    ingestor.run()


if __name__ == '__main__':
    main()
