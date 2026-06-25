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
    """
    Handles read operations and initial splitting of the raw transactional dataset.
    Exposes distinct datasets for customers, products, and order transactions.
    """

    def __init__(self, spark: SparkSession, logger: logging.Logger):
        self.spark = spark
        self.logger = logger

    def get_raw_schema(self) -> StructType:
        """Defines the explicit schema for the raw CSV data."""
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
        """Reads raw transactional data from the given S3/Local path with explicit schema."""
        self.logger.info(f"Ingesting raw transactions from: {file_path}")
        schema = self.get_raw_schema()

        # Read from CSV with schema, header true
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
        """
        Splits the raw DataFrame into three working DataFrames:
        1. customers (distinct Customer ID and Country)
        2. products (distinct StockCode and Description)
        3. orders (transaction lines mapped to Customer ID and StockCode)
        """
        self.logger.info(
            "Splitting raw dataset into customers, products, and orders extracts..."
        )

        # 1. Customers Extract: distinct Customer ID and Country
        # Note: We filter out null Customer IDs for customer database dimension mapping
        customers_df = (
            raw_df.select(
                F.col("Customer ID").cast(IntegerType()).alias("customer_id"),
                F.col("Country").alias("country"),
            )
            .filter(F.col("customer_id").isNotNull())
            .distinct()
        )

        # 2. Products Extract: distinct StockCode and Description
        # Note: Filter out null StockCodes. Keep descriptions for mapping.
        products_df = (
            raw_df.select(
                F.col("StockCode").alias("stock_code"),
                F.col("Description").alias("description"),
            )
            .filter(F.col("stock_code").isNotNull())
            .distinct()
        )

        # 3. Orders Extract: Near-direct carry-over of transaction rows with structured names
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
