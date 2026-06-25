import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Task8CleanText")

spark = SparkSession.builder \
    .appName("Task8-Clean-Text") \
    .getOrCreate()

# Resolve local path
csv_abs_path = "file://" + os.path.abspath("data/raw/online_retail_II.csv")
df = spark.read.option("header", "true").csv(csv_abs_path)

# Standardize: trim, initcap
clean_df = df \
    .withColumn("Description", F.initcap(F.trim(F.col("Description")))) \
    .withColumn("Country", F.initcap(F.trim(F.col("Country"))))

clean_df.select("Description", "Country").show(5)

spark.stop()
