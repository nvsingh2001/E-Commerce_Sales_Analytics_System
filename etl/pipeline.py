import os
from config.settings import Settings
from etl.base_pipeline import BaseETLPipeline
from etl.extraction.extractor import DataExtractor
from etl.transformation.transformer import DataTransformer
from etl.loading.loader import DataLoader

class EcommerceSalesAnalyticsPipeline(BaseETLPipeline):
    """
    Concrete implementation of the E-Commerce Sales Analytics ETL Pipeline.
    Manages coordination between extraction, transformation, and loading layers.
    """
    def __init__(self):
        super().__init__("EcommerceSalesAnalyticsPipeline")
        
        # Pull S3 Bucket from settings
        self.s3_bucket = Settings.S3_BUCKET
        
        # Determine whether to read from S3 bucket or local directories
        if self.s3_bucket:
            self.input_path = f"s3a://{self.s3_bucket}/raw/online_retail_II.csv"
            self.curated_bucket = self.s3_bucket
        else:
            self.input_path = "data/raw/online_retail_II.csv"
            self.curated_bucket = "data/curated"

    def extract(self) -> dict:
        """Extracts data and returns customer, product, and transaction line items."""
        extractor = DataExtractor(self.spark, self.logger)
        raw_df = extractor.extract_raw_data(self.input_path)
        return extractor.split_extracts(raw_df)

    def transform(self, dataframes: dict) -> dict:
        """Transforms data, validates quality rules, and aggregates analytics summaries."""
        transformer = DataTransformer(self.logger)
        
        # Step A: Clean and standardize text columns
        standardized_dfs = transformer.standardize_and_clean_data(dataframes)
        orders = standardized_dfs["orders"]
        
        # Step B: Apply Data Quality strategy validations
        valid_orders, rejected_orders = transformer.validate_data_quality(orders)
        
        # Step C: Deduplicate orders
        clean_orders, duplicate_orders = transformer.deduplicate_orders(valid_orders)
        
        # Update orders mapping to clean data
        standardized_dfs["orders"] = clean_orders
        
        # Step D: Enforce Star Schema joins, RFM segment scores, and pre-aggregate analytics summaries
        reporting_tables = transformer.build_reporting_tables(standardized_dfs)
        
        # Save rejected records and duplicates in dictionary for Loading
        reporting_tables["rejected_orders"] = rejected_orders
        reporting_tables["duplicate_orders"] = duplicate_orders
        
        return reporting_tables

    def load(self, transformed_dfs: dict) -> None:
        """Saves DataFrames into S3 Curated Zone (Parquet) and loads RDS PostgreSQL."""
        loader = DataLoader(self.logger)
        
        # 1. Load data to RDS Postgres & S3 (curated facts/dimensions/analytics)
        loader.load_pipeline_data(self.spark, transformed_dfs, self.curated_bucket)
        
        # 2. Write audit data (rejected and duplicates) to S3 curated folder in Parquet format
        loader.write_to_s3_parquet(transformed_dfs["rejected_orders"], self.curated_bucket, "audit/rejected_orders")
        loader.write_to_s3_parquet(transformed_dfs["duplicate_orders"], self.curated_bucket, "audit/duplicate_orders")

if __name__ == "__main__":
    pipeline = EcommerceSalesAnalyticsPipeline()
    pipeline.run()
