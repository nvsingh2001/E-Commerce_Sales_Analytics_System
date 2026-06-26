import logging
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from repositories.database_repository import DatabaseRepository
from repositories.database_connector import DatabaseConnector
from config.settings import Settings


class DataLoader:
    def __init__(self, spark: SparkSession, logger: logging.Logger, db_connector: DatabaseConnector = None):
        self.spark = spark
        self.logger = logger
        self._db_connector = db_connector or DatabaseConnector()

    def write_to_s3_parquet(
        self,
        df: DataFrame,
        bucket_name: str,
        key_prefix: str,
        partition_by_date: bool = False,
    ) -> None:
        s3_path = (
            f"s3a://{bucket_name}/{key_prefix}"
            if not bucket_name.startswith(".") and not bucket_name.startswith("/")
            else f"{bucket_name}/{key_prefix}"
        )
        self.logger.info(f"Writing Parquet data to S3 path: {s3_path}")

        try:
            write_spec = df.write.mode("overwrite")

            if partition_by_date and "order_date" in df.columns:
                df_partitioned = df.withColumn(
                    "year_month", F.date_format(F.col("order_date"), "yyyy-MM")
                )
                write_spec = df_partitioned.write.mode("overwrite").partitionBy(
                    "year_month"
                )
                write_spec.parquet(s3_path)
            else:
                write_spec.parquet(s3_path)

            self.logger.info(f"Successfully wrote Parquet file to S3: {s3_path}")
        except Exception as e:
            self.logger.error(f"Error writing Parquet to S3: {e}")
            raise e

    def save_to_s3(self, transformed_dfs: dict, bucket_name: str) -> None:
        self.logger.info("Writing dimensions to S3 Parquet...")
        self.write_to_s3_parquet(
            transformed_dfs["dim_customers"], bucket_name, "dim_customers"
        )
        self.write_to_s3_parquet(
            transformed_dfs["dim_products"], bucket_name, "dim_products"
        )

        self.logger.info("Writing fact and analytics tables to S3 Parquet...")
        self.write_to_s3_parquet(
            transformed_dfs["fact_orders"], bucket_name, "fact_orders", partition_by_date=True
        )
        self.write_to_s3_parquet(
            transformed_dfs["revenue_summary"], bucket_name, "analytics/revenue_summary"
        )
        self.write_to_s3_parquet(
            transformed_dfs["customer_retention"], bucket_name, "analytics/customer_retention"
        )
        self.write_to_s3_parquet(
            transformed_dfs["product_performance"], bucket_name, "analytics/product_performance"
        )

    def load_pipeline_data(self, transformed_dfs: dict) -> None:
        db_repo = DatabaseRepository(self.spark, self._db_connector)

        self.logger.info("Truncating all target database tables...")
        db_repo.truncate_all_tables()

        self.logger.info("Loading dimension tables to PostgreSQL RDS...")
        db_repo.load_table(
            transformed_dfs["dim_customers"], Settings.TABLE_NAMES["dim_customers"]
        )
        db_repo.load_table(
            transformed_dfs["dim_products"], Settings.TABLE_NAMES["dim_products"]
        )

        self.logger.info("Loading fact_orders to PostgreSQL RDS...")
        db_repo.load_table(
            transformed_dfs["fact_orders"], Settings.TABLE_NAMES["fact_orders"]
        )

        self.logger.info("Loading analytics tables to PostgreSQL RDS...")
        db_repo.load_table(
            transformed_dfs["revenue_summary"], Settings.TABLE_NAMES["revenue_summary"]
        )
        db_repo.load_table(
            transformed_dfs["customer_retention"],
            Settings.TABLE_NAMES["customer_retention"],
        )
        db_repo.load_table(
            transformed_dfs["product_performance"],
            Settings.TABLE_NAMES["product_performance"],
        )

        self.logger.info(
            "All pipeline data successfully loaded to RDS database."
        )
