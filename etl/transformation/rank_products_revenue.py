import os
import logging
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task7ProductRank")

spark = SparkSession.builder \
    .appName("Task7-Product-Ranking") \
    .getOrCreate()

# Resolve local path
csv_abs_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")

# Load raw dataset
df = spark.read.option("header", "true").csv(csv_abs_path) \
    .withColumn("Quantity", F.col("Quantity").cast("integer")) \
    .withColumn("Price", F.col("Price").cast("double"))

# Completed orders
completed_orders = df.filter(~F.col("Invoice").startswith("C"))

# Group by product
product_sales = completed_orders.groupBy("StockCode").agg(
    F.round(F.sum(F.col("Quantity") * F.col("Price")), 2).alias("total_revenue")
)

# Rank overall
window_spec = Window.orderBy(F.col("total_revenue").desc())
ranked_products = product_sales.withColumn("overall_rank", F.dense_rank().over(window_spec))

ranked_products.show(10)

spark.stop()
