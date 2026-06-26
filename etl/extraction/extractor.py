import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
    TimestampType,
)
from pyspark.sql import functions as F


class DataExtractor:
    def __init__(self, spark: SparkSession, logger: logging.Logger):
        self.spark = spark
        self.logger = logger

    def get_raw_schema(self) -> StructType:
        return StructType(
            [
                StructField("Invoice", StringType(), True),
                StructField("StockCode", StringType(), True),
                StructField("Description", StringType(), True),
                StructField("Quantity", IntegerType(), True),
                StructField("InvoiceDate", TimestampType(), True),
                StructField("Price", DoubleType(), True),
                StructField("Customer ID", DoubleType(), True),
                StructField("Country", StringType(), True),
            ]
        )

    def extract_raw_data(self, file_path: str) -> DataFrame:
        self.logger.info(f"Ingesting raw transactions from: {file_path}")
        schema = self.get_raw_schema()

        df = (
            self.spark.read.format("csv")
            .option("header", "true")
            .schema(schema)
            .load(file_path)
        )

        row_count = df.count()
        self.logger.info(f"Ingestion complete. Read {row_count} rows from raw dataset.")
        return df

    def split_extracts(self, raw_df: DataFrame) -> dict:
        self.logger.info(
            "Splitting raw dataset into customers, products, and orders extracts..."
        )

        customers_df = (
            raw_df.select(
                F.col("Customer ID").cast(IntegerType()).alias("customer_id"),
                F.col("Country").alias("country"),
            )
            .filter(F.col("customer_id").isNotNull())
            .distinct()
        )

        products_df = (
            raw_df.select(
                F.col("StockCode").alias("stock_code"),
                F.col("Description").alias("description"),
            )
            .filter(F.col("stock_code").isNotNull())
            .distinct()
        )

        orders_df = raw_df.select(
            F.col("Invoice").alias("invoice_no"),
            F.col("Customer ID").cast(IntegerType()).alias("customer_id"),
            F.col("StockCode").alias("stock_code"),
            F.col("InvoiceDate").alias("order_date"),
            F.col("Quantity").alias("quantity"),
            F.col("Price").alias("unit_price"),
        )

        customers_count = customers_df.count()
        products_count = products_df.count()
        orders_count = orders_df.count()

        self.logger.info(
            f"Splitting complete. Row counts: "
            f"customers: {customers_count}, "
            f"products: {products_count}, "
            f"orders: {orders_count}"
        )

        return {"customers": customers_df, "products": products_df, "orders": orders_df}
