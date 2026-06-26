import logging
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


class RFMSegmenter:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def compute_segments(self, orders_df: DataFrame) -> DataFrame:
        self.logger.info("Computing RFM customer segments...")

        completed_orders = orders_df.filter(
            (F.col("customer_id").isNotNull()) & (~F.col("invoice_no").startswith("C"))
        )

        max_date_row = completed_orders.select(F.max("order_date")).collect()
        if not max_date_row or not max_date_row[0][0]:
            self.logger.warning("No orders found. Assigning default 'New' segment.")
            return (
                completed_orders.select("customer_id")
                .distinct()
                .withColumn("customer_segment", F.lit("New"))
            )

        max_dataset_date = max_date_row[0][0]
        self.logger.info(
            f"Using reference date for recency calculation: {max_dataset_date}"
        )

        customer_aggregates = completed_orders.groupBy("customer_id").agg(
            F.max("order_date").alias("last_order_date"),
            F.countDistinct("invoice_no").alias("frequency"),
            F.sum(F.col("quantity") * F.col("unit_price")).alias("monetary"),
        )

        customer_metrics = customer_aggregates.withColumn(
            "recency_days",
            F.datediff(F.lit(max_dataset_date), F.col("last_order_date")),
        )

        w_recency = Window.orderBy(F.col("recency_days").desc())
        w_frequency = Window.orderBy(F.col("frequency").asc())
        w_monetary = Window.orderBy(F.col("monetary").asc())

        scored_df = (
            customer_metrics.withColumn("r_score", F.ntile(5).over(w_recency))
            .withColumn("f_score", F.ntile(5).over(w_frequency))
            .withColumn("m_score", F.ntile(5).over(w_monetary))
        )

        segmented_df = scored_df.withColumn(
            "customer_segment",
            F.when(
                (F.col("r_score") >= 4)
                & (F.col("f_score") >= 4)
                & (F.col("m_score") >= 4),
                F.lit("Champions"),
            )
            .when((F.col("f_score") >= 3) & (F.col("m_score") >= 3), F.lit("Loyal"))
            .when((F.col("r_score") >= 4) & (F.col("f_score") <= 2), F.lit("New"))
            .when((F.col("r_score") <= 2) & (F.col("f_score") >= 3), F.lit("At Risk"))
            .when((F.col("r_score") <= 2) & (F.col("f_score") <= 2), F.lit("Lapsed"))
            .otherwise(F.lit("Repeat")),
        )

        self.logger.info("RFM customer segment computation complete.")
        return segmented_df.select("customer_id", "customer_segment")
