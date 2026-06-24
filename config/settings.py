from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")

    DB_NAME = os.getenv("DB_NAME", "ecommerce_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    S3_BUCKET = os.getenv("S3_BUCKET")