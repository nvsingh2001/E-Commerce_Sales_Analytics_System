import os
import logging
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from repositories.database_repository import DatabaseRepository


class DataLoader:
    """
    Coordinates data writes to Amazon S3 (Parquet) and AWS RDS PostgreSQL.
    Retrieves generated database surrogate keys and maps fact tables to preserve integrity.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def write_to_s3_parquet(
        self,
        df: DataFrame,
        bucket_name: str,
        key_prefix: str,
        partition_by_date: bool = False,
    ) -> None:
        """Writes PySpark DataFrame to S3 (or local path simulating S3) in Parquet format."""
        s3_path = (
            f"s3a://{bucket_name}/{key_prefix}"
            if not bucket_name.startswith(".") and not bucket_name.startswith("/")
            else f"{bucket_name}/{key_prefix}"
        )
        self.logger.info(f"Writing Parquet data to S3 path: {s3_path}")

        try:
            write_spec = df.write.mode("overwrite")

            if partition_by_date and "order_date" in df.columns:
                # Add year-month derived column for partitioning
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

    def load_pipeline_data(
        self, spark_session, transformed_dfs: dict, bucket_name: str
    ) -> None:
        """
        Loads dimensions, fact, and analytics tables directly into S3 Parquet
        and AWS RDS PostgreSQL, since the schema uses natural keys.
        """
        db_repo = DatabaseRepository(spark_session)

        # Truncate all tables first to handle foreign key dependencies cleanly
        self.logger.info("Truncating all target database tables...")
        db_repo.truncate_all_tables()

        # 1. Load Dimension Tables into PostgreSQL
        self.logger.info("Loading dimension tables to PostgreSQL RDS...")
        db_repo.load_table(transformed_dfs["dim_customers"], "dim_customers")
        db_repo.load_table(transformed_dfs["dim_products"], "dim_products")

        # 2. Write dimensions to S3 Parquet
        self.logger.info("Writing dimensions to S3 Parquet...")
        self.write_to_s3_parquet(
            transformed_dfs["dim_customers"], bucket_name, "dim_customers"
        )
        self.write_to_s3_parquet(
            transformed_dfs["dim_products"], bucket_name, "dim_products"
        )

        # 3. Load fact table into PostgreSQL RDS
        self.logger.info("Loading fact_orders to PostgreSQL RDS...")
        db_repo.load_table(transformed_dfs["fact_orders"], "fact_orders")

        # 4. Load analytics tables into PostgreSQL RDS
        self.logger.info("Loading analytics tables to PostgreSQL RDS...")
        db_repo.load_table(transformed_dfs["revenue_summary"], "analytics.revenue_summary")
        db_repo.load_table(transformed_dfs["customer_retention"], "analytics.customer_retention")
        db_repo.load_table(transformed_dfs["product_performance"], "analytics.product_performance")

        # 5. Write fact and analytics tables to S3 Parquet
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

        # Log write audits
        self.logger.info(
            "All pipeline data successfully loaded to RDS database and S3."
        )
