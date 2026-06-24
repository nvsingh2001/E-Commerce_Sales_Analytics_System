import boto3

from config.settings import Settings


class S3Service:

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            region_name=Settings.AWS_REGION
        )

    def create_bucket(self, bucket_name: str):

        response = self.s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                "LocationConstraint": Settings.AWS_REGION
            }
        )

        return response

    def bucket_exists(self, bucket_name: str):

        try:
            self.s3_client.head_bucket(
                Bucket=bucket_name
            )
            return True

        except Exception:
            return False

    def create_folder_structure(
        self,
        bucket_name: str
    ):

        self.s3_client.put_object(
            Bucket=bucket_name,
            Key="raw/"
        )

        self.s3_client.put_object(
            Bucket=bucket_name,
            Key="curated/"
        )

    def upload_file(
        self,
        file_path: str,
        bucket_name: str,
        key: str
    ):

        self.s3_client.upload_file(
            file_path,
            bucket_name,
            key
        )