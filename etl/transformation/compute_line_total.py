import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task4LineTotal")

spark = SparkSession.builder \
    .appName("Task4-Line-Total") \
    .getOrCreate()

# Resolve local path
csv_abs_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")

# Read raw data
df = spark.read.option("header", "true").csv(csv_abs_path) \
    .withColumn("Quantity", F.col("Quantity").cast("integer")) \
    .withColumn("Price", F.col("Price").cast("double"))

# Compute revenue / line_total
df_with_total = df.withColumn(
    "revenue", 
    F.round(F.col("Quantity") * F.col("Price"), 2)
)

df_with_total.select("Invoice", "Quantity", "Price", "revenue").show(5)

spark.stop()
