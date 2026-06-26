import logging
import time
from abc import ABC, abstractmethod
from pyspark.sql import SparkSession
from config.settings import Settings


class PipelineLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        class_name = self.extra.get("class_name", "ETLPipeline")
        return f"[{class_name}] {msg}", kwargs


class BaseETLPipeline(ABC):
    _logging_configured = False

    def __init__(self, app_name: str):
        if not BaseETLPipeline._logging_configured:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
            )
            BaseETLPipeline._logging_configured = True

        self.app_name = app_name
        self.logger = PipelineLoggerAdapter(
            logging.getLogger(self.__class__.__name__),
            {"class_name": self.__class__.__name__},
        )
        self.spark = None

    def _init_spark_session(self) -> SparkSession:
        self.logger.info("Initializing Spark session...")
        spark = (
            SparkSession.builder.appName(self.app_name)
            .config("spark.jars.packages", Settings.SPARK_PACKAGES)
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
        pass

    @abstractmethod
    def transform(self, dataframes: dict) -> dict:
        pass

    @abstractmethod
    def load(self, transformed_dfs: dict) -> None:
        pass

    def run(self) -> None:
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
