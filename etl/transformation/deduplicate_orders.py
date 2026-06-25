import os
import logging
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task5Deduplicate")

spark = SparkSession.builder \
    .appName("Task5-Deduplicate") \
    .getOrCreate()

# Resolve local path
csv_abs_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")
df = spark.read.option("header", "true").csv(csv_abs_path)

# Window Spec partitioned by Invoice, StockCode, Quantity, and InvoiceDate
window_spec = Window.partitionBy("Invoice", "StockCode", "Quantity", "InvoiceDate").orderBy("Invoice")

df_row_num = df.withColumn("row_num", F.row_number().over(window_spec))

# Deduplicate
clean_df = df_row_num.filter(F.col("row_num") == 1).drop("row_num")
duplicate_df = df_row_num.filter(F.col("row_num") > 1).drop("row_num")

logger.info(f"Row count before: {df.count()}")
logger.info(f"Clean row count: {clean_df.count()}")
logger.info(f"Removed duplicates: {duplicate_df.count()}")

spark.stop()
