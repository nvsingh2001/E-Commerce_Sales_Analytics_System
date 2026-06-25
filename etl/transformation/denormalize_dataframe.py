import os
import logging
from pyspark.sql import SparkSession
from etl.extraction.extractor import DataExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task3Join")

spark = SparkSession.builder \
    .appName("Task3-Join-Extracts") \
    .getOrCreate()

extractor = DataExtractor(spark, logger)

# Resolve local path
input_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")

# Extract and Split
raw_df = extractor.extract_raw_data(input_path)
extracts = extractor.split_extracts(raw_df)

# Perform join
denormalized_df = extracts["orders"] \
    .join(extracts["customers"], "customer_id", "inner") \
    .join(extracts["products"], "stock_code", "inner")

logger.info(f"Joined denormalized row count: {denormalized_df.count()}")
denormalized_df.show(5)

spark.stop()
