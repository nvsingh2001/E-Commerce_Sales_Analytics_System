import logging
import time
from abc import ABC, abstractmethod
from pyspark.sql import SparkSession
from config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class PipelineLoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter to inject the class name into log formatting."""

    def process(self, msg, kwargs):
        class_name = self.extra.get("class_name", "ETLPipeline")
        return f"[{class_name}] {msg}", kwargs


class BaseETLPipeline(ABC):
    """
    Abstract base class for all ETL pipelines implementing the Template Method Pattern.
    It governs the lifecycle of Spark ETL runs (Extract, Transform, Load).
    """

    def __init__(self, app_name: str):
        self.app_name = app_name
        self.logger = PipelineLoggerAdapter(
            logging.getLogger(self.__class__.__name__),
            {"class_name": self.__class__.__name__},
        )
        self.spark = None

    def _init_spark_session(self) -> SparkSession:
        """
        Initializes the PySpark session. Injects AWS S3A connectors and PostgreSQL JDBC drivers.
        """
        self.logger.info("Initializing Spark session...")
        # Incorporate hadoop-aws for S3 integration and postgresql driver for database connectivity
        spark = (
            SparkSession.builder.appName(self.app_name)
            .config(
                "spark.jars.packages",
                "org.apache.hadoop:hadoop-aws:3.4.1,org.postgresql:postgresql:42.7.2",
            )
            .config(
                "spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
            )
            .config(
                "spark.hadoop.fs.s3a.aws.credentials.provider",
                "software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider",
            )
            .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
            .getOrCreate()
        )

        self.logger.info("Spark session successfully initialized.")
        return spark

    @abstractmethod
    def extract(self) -> dict:
        """
        Extract stage: reads raw data and returns a dictionary of PySpark DataFrames.
        Must be implemented by concrete subclasses.
        """
        pass

    @abstractmethod
    def transform(self, dataframes: dict) -> dict:
        """
        Transform stage: cleans, standardizes, enriches, and aggregates data.
        Must be implemented by concrete subclasses.
        """
        pass

    @abstractmethod
    def load(self, transformed_dfs: dict) -> None:
        """
        Load stage: writes data to S3 curated Parquet and AWS RDS PostgreSQL.
        Must be implemented by concrete subclasses.
        """
        pass

    def run(self) -> None:
        """
        The Template Method defining the skeleton of the ETL pipeline execution.
        """
        self.logger.info(f"Starting ETL Pipeline: {self.app_name}")
        start_time = time.time()

        try:
            self.spark = self._init_spark_session()

            self.logger.info("Starting extraction stage...")
            raw_data = self.extract()
            self.logger.info("Extraction stage completed.")

            self.logger.info("Starting transformation stage...")
            transformed_data = self.transform(raw_data)
            self.logger.info("Transformation stage completed.")

            self.logger.info("Starting loading stage...")
            self.load(transformed_data)
            self.logger.info("Loading stage completed.")

            duration = time.time() - start_time
            self.logger.info(
                f"ETL Pipeline '{self.app_name}' completed successfully in {duration:.2f} seconds."
            )

        except Exception as e:
            self.logger.error(f"ETL Pipeline execution failed: {e}", exc_info=True)
            raise e
        finally:
            if self.spark:
                self.logger.info("Stopping Spark Session...")
                self.spark.stop()
                self.logger.info("Spark Session stopped.")
