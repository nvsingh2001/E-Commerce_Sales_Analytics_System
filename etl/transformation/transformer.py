import logging
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from etl.transformation.rules import (
    NullCheckRule,
    QuantityRangeRule,
    UnitPriceRangeRule,
    InvoiceDateWindowRule,
)
from etl.transformation.rfm import RFMSegmenter
from config.settings import Settings


class DataTransformer:
    def __init__(
        self, logger: logging.Logger, validation_rules=None, rfm_segmenter=None
    ):
        self.logger = logger
        self.rfm_segmenter = rfm_segmenter or RFMSegmenter(logger)
        self.validation_rules = validation_rules or [
            NullCheckRule(["invoice_no", "stock_code"]),
            QuantityRangeRule(),
            UnitPriceRangeRule(),
            InvoiceDateWindowRule(),
        ]

    def standardize_and_clean_data(self, raw_dfs: dict) -> dict:
        self.logger.info("Standardizing and cleaning text fields...")

        customers = raw_dfs["customers"]
        products = raw_dfs["products"]
        orders = raw_dfs["orders"]

        clean_customers = customers.withColumn(
            "country", F.initcap(F.trim(F.col("country")))
        )

        clean_products = products.withColumn(
            "description",
            F.when(
                F.col("description").isNull() | (F.trim(F.col("description")) == ""),
                F.lit("Unknown Product"),
            ).otherwise(F.initcap(F.trim(F.col("description")))),
        )

        return {
            "customers": clean_customers,
            "products": clean_products,
            "orders": orders,
        }

    def validate_data_quality(self, orders_df: DataFrame) -> tuple:
        self.logger.info("Executing Data Quality Validation Rules...")

        flagged_df = orders_df
        for rule in self.validation_rules:
            flagged_df = rule.validate(flagged_df)

        validation_cols = [c for c in flagged_df.columns if c.startswith("is_valid_")]

        valid_condition = F.lit(True)
        for col in validation_cols:
            valid_condition = valid_condition & (F.col(col) == True)

        valid_orders = flagged_df.filter(valid_condition).drop(*validation_cols)
        rejected_orders = flagged_df.filter(~valid_condition)

        valid_count = valid_orders.count()
        rejected_count = rejected_orders.count()
        self.logger.info(
            f"Validation complete. Valid rows: {valid_count}, Rejected rows: {rejected_count}"
        )

        return valid_orders, rejected_orders

    def deduplicate_orders(self, orders_df: DataFrame) -> tuple:
        self.logger.info("Deduplicating transaction records...")

        window_spec = Window.partitionBy(
            "invoice_no", "stock_code", "quantity", "order_date"
        ).orderBy("invoice_no")

        df_row_num = orders_df.withColumn("row_num", F.row_number().over(window_spec))

        clean_orders = df_row_num.filter(F.col("row_num") == 1).drop("row_num")
        duplicate_orders = df_row_num.filter(F.col("row_num") > 1).drop("row_num")

        clean_count = clean_orders.count()
        dup_count = duplicate_orders.count()
        self.logger.info(
            f"Deduplication complete. Retained: {clean_count}, Removed duplicates: {dup_count}"
        )

        return clean_orders, duplicate_orders

    def build_reporting_tables(self, cleaned_dfs: dict) -> dict:
        self.logger.info(
            "Building dimensional fact and aggregated analytics DataFrames..."
        )

        customers = cleaned_dfs["customers"]
        products = cleaned_dfs["products"]
        orders = cleaned_dfs["orders"]

        enriched_orders = orders.withColumn(
            "line_total", F.round(F.col("quantity") * F.col("unit_price"), 2)
        ).withColumn(
            "order_status",
            F.when(F.col("invoice_no").startswith("C"), F.lit("Cancelled")).otherwise(
                F.lit("Completed")
            ),
        )

        fact_orders = enriched_orders.select(
            F.col("invoice_no").alias("order_id"),
            F.col("customer_id"),
            F.col("stock_code").alias("product_id"),
            F.col("order_date"),
            F.col("quantity"),
            F.col("unit_price"),
            F.col("line_total"),
            F.col("order_status"),
        )

        avg_prices = (
            enriched_orders.filter(F.col("order_status") == "Completed")
            .groupBy("stock_code")
            .agg(F.round(F.mean("unit_price"), 2).alias("avg_unit_price"))
        )

        dim_products = products.join(avg_prices, "stock_code", "left").withColumn(
            "avg_unit_price", F.coalesce(F.col("avg_unit_price"), F.lit(0.00))
        )

        w_prod_desc = Window.partitionBy("stock_code").orderBy(
            F.col("description").desc()
        )
        dim_products = (
            dim_products.withColumn("row_num", F.row_number().over(w_prod_desc))
            .filter(F.col("row_num") == 1)
            .select(
                F.col("stock_code").alias("product_id"),
                F.col("description").alias("product_name"),
                F.col("avg_unit_price"),
            )
        )

        customer_segments = self.rfm_segmenter.compute_segments(enriched_orders)
        dim_customers = customers.join(customer_segments, "customer_id", "left")

        w_cust_country = Window.partitionBy("customer_id").orderBy(
            F.col("country").desc()
        )
        dim_customers = (
            dim_customers.withColumn("row_num", F.row_number().over(w_cust_country))
            .filter(F.col("row_num") == 1)
            .select(F.col("customer_id"), F.col("country"), F.col("customer_segment"))
        )

        completed_orders = enriched_orders.filter(F.col("order_status") == "Completed")

        revenue_summary = (
            completed_orders.join(dim_customers, "customer_id", "inner")
            .withColumn(
                "month", F.date_trunc("month", F.col("order_date")).cast("date")
            )
            .groupBy("country", "month")
            .agg(
                F.countDistinct("invoice_no").alias("total_orders"),
                F.round(F.sum("line_total"), 2).alias("total_revenue"),
            )
            .withColumn(
                "average_order_value",
                F.round(F.col("total_revenue") / F.col("total_orders"), 2),
            )
            .select(
                "country",
                "month",
                "total_revenue",
                "total_orders",
                "average_order_value",
            )
        )

        retention_base = (
            completed_orders.filter(F.col("customer_id").isNotNull())
            .groupBy("customer_id")
            .agg(
                F.countDistinct("invoice_no").alias("total_orders"),
                F.round(F.sum("line_total"), 2).alias("lifetime_spend"),
                F.min(F.col("order_date")).cast("date").alias("first_order_date"),
                F.max(F.col("order_date")).cast("date").alias("last_order_date"),
            )
        )

        max_date_row = completed_orders.select(F.max("order_date")).collect()
        max_dataset_date = (
            max_date_row[0][0] if max_date_row and max_date_row[0][0] else None
        )

        if max_dataset_date:
            customer_retention = retention_base.withColumn(
                "customer_status",
                F.when(F.col("total_orders") == 1, F.lit("New"))
                .when(
                    F.datediff(F.lit(max_dataset_date), F.col("last_order_date"))
                    > Settings.LAPSED_THRESHOLD_DAYS,
                    F.lit("Lapsed"),
                )
                .otherwise(F.lit("Repeat")),
            )
        else:
            customer_retention = retention_base.withColumn(
                "customer_status",
                F.when(F.col("total_orders") == 1, F.lit("New")).otherwise(
                    F.lit("Repeat")
                ),
            )

        customer_retention = customer_retention.select(
            "customer_id",
            "total_orders",
            "lifetime_spend",
            "first_order_date",
            "last_order_date",
            "customer_status",
        )

        product_performance = (
            completed_orders.withColumn(
                "month", F.date_trunc("month", F.col("order_date")).cast("date")
            )
            .groupBy("stock_code", "month")
            .agg(
                F.sum("quantity").alias("units_sold"),
                F.round(F.sum("line_total"), 2).alias("total_revenue"),
            )
        )

        window_rank = Window.partitionBy("month").orderBy(F.col("total_revenue").desc())
        product_performance = product_performance.withColumn(
            "overall_rank", F.dense_rank().over(window_rank)
        ).select(
            F.col("stock_code").alias("product_id"),
            F.col("month"),
            F.col("units_sold"),
            F.col("total_revenue"),
            F.col("overall_rank"),
        )

        return {
            "dim_customers": dim_customers,
            "dim_products": dim_products,
            "fact_orders": fact_orders,
            "revenue_summary": revenue_summary,
            "customer_retention": customer_retention,
            "product_performance": product_performance,
        }

    def transform_all(self, raw_dfs: dict) -> dict:
        cleaned_dfs = self.standardize_and_clean_data(raw_dfs)
        valid_orders, rejected_orders = self.validate_data_quality(
            cleaned_dfs["orders"]
        )
        clean_orders, duplicate_orders = self.deduplicate_orders(valid_orders)
        cleaned_dfs["orders"] = clean_orders
        return self.build_reporting_tables(cleaned_dfs)
