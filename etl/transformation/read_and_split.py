import os
import logging
from pyspark.sql import SparkSession
from etl.extraction.extractor import DataExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task1Split")

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Task1-Split-Dataset") \
    .getOrCreate()

extractor = DataExtractor(spark, logger)

# Set absolute local file path with file:// scheme
input_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")

# Ingest and Split
raw_df = extractor.extract_raw_data(input_path)
extracts = extractor.split_extracts(raw_df)

# Show samples of split dataframes
logger.info("Customers sample:")
extracts["customers"].show(5)

logger.info("Products sample:")
extracts["products"].show(5)

logger.info("Orders sample:")
extracts["orders"].show(5)

spark.stop()
