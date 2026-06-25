from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task2Filter")

spark = SparkSession.builder \
    .appName("Task2-Filter-Zero-Quantity") \
    .getOrCreate()

# Read orders extract
import os
csv_abs_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")
df = spark.read.option("header", "true").csv(csv_abs_path)

logger.info(f"Total row count before filter: {df.count()}")

# Filter out zero quantity
filtered_df = df.filter(F.col("Quantity") != 0)

logger.info(f"Total row count after filter: {filtered_df.count()}")
filtered_df.show(5)

spark.stop()
