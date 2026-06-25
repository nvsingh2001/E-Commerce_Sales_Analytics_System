import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task9OrderStatus")

spark = SparkSession.builder \
    .appName("Task9-Order-Status") \
    .getOrCreate()

# Resolve local path
csv_abs_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")
df = spark.read.option("header", "true").csv(csv_abs_path)

# Derive status
df_with_status = df.withColumn(
    "order_status",
    F.when(F.col("Invoice").startswith("C"), F.lit("Cancelled"))
    .otherwise(F.lit("Completed"))
)

df_with_status.select("Invoice", "order_status").distinct().show(10)

spark.stop()
