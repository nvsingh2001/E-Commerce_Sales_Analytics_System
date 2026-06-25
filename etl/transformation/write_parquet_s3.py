import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task10WriteParquet")

spark = SparkSession.builder.appName("Task10-Write-Parquet").getOrCreate()

csv_abs_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")
curated_path = "file://" + os.path.abspath("data/curated/fact_orders_mock")

df = (
    spark.read.option("header", "true")
    .csv(csv_abs_path)
    .withColumn("order_date", F.to_timestamp(F.col("InvoiceDate")))
)

df_partitioned = df.withColumn(
    "year_month", F.date_format(F.col("order_date"), "yyyy-MM")
)

logger.info(f"Writing partitioned Parquet files to {curated_path}...")
df_partitioned.write.mode("overwrite").partitionBy("year_month").parquet(curated_path)

logger.info("Curated Parquet write completed.")

spark.stop()
