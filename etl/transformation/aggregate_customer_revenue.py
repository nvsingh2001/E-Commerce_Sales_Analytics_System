import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task6CustomerAgg")

spark = SparkSession.builder.appName("Task6-Customer-Aggregates").getOrCreate()

csv_abs_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")

df = (
    spark.read.option("header", "true")
    .csv(csv_abs_path)
    .withColumn("Quantity", F.col("Quantity").cast("integer"))
    .withColumn("Price", F.col("Price").cast("double"))
    .withColumn("Customer ID", F.col("Customer ID").cast("double").cast("integer"))
)

completed_orders = df.filter(
    (F.col("Customer ID").isNotNull()) & (~F.col("Invoice").startswith("C"))
)

customer_aggregates = completed_orders.groupBy("Customer ID").agg(
    F.countDistinct("Invoice").alias("total_orders"),
    F.round(F.sum(F.col("Quantity") * F.col("Price")), 2).alias("lifetime_spend"),
)

customer_aggregates.show(5)

spark.stop()
