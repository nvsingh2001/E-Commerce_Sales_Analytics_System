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

    S3_BUCKET = os.getenv("S3_BUCKET_NAME") or os.getenv("S3_BUCKET")

    SPARK_PACKAGES = os.getenv(
        "SPARK_PACKAGES",
        "org.apache.hadoop:hadoop-aws:3.4.1,org.postgresql:postgresql:42.7.2"
    )

    LOCAL_RAW_PATH = os.getenv("LOCAL_RAW_PATH", "data/raw/online_retail_II.csv")
    LOCAL_CURATED_PATH = os.getenv("LOCAL_CURATED_PATH", "data/curated")

    LAPSED_THRESHOLD_DAYS = int(os.getenv("LAPSED_THRESHOLD_DAYS", "180"))

    DATASET_START_DATE = os.getenv("DATASET_START_DATE", "2009-12-01 00:00:00")
    DATASET_END_DATE = os.getenv("DATASET_END_DATE", "2011-12-31 23:59:59")

    DATASET_URL = os.getenv(
        "DATASET_URL",
        "https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx"
    )

    TABLE_NAMES = {
        "dim_customers": "dim_customers",
        "dim_products": "dim_products",
        "fact_orders": "fact_orders",
        "revenue_summary": "analytics.revenue_summary",
        "customer_retention": "analytics.customer_retention",
        "product_performance": "analytics.product_performance",
    }

    TABLE_LABELS = {
        "dim_customers": "Dimension - Customers",
        "dim_products": "Dimension - Products",
        "fact_orders": "Fact - Orders",
        "analytics.revenue_summary": "Reporting - Revenue Summary",
        "analytics.customer_retention": "Reporting - Customer Retention",
        "analytics.product_performance": "Reporting - Product Performance",
    }
