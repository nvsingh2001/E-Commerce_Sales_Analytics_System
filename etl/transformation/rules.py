from abc import ABC, abstractmethod
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

class ValidationRule(ABC):
    """
    Abstract Strategy class for Data Quality Validation Rules.
    Each rule applies a check to a PySpark DataFrame and adds a verification flag column.
    """
    @abstractmethod
    def validate(self, df: DataFrame) -> DataFrame:
        """
        Applies validation check to the DataFrame.
        Adds a boolean column `is_valid_<rule_name>` indicating if the row passed the check.
        """
        pass

class NullCheckRule(ValidationRule):
    """
    Checks that the specified columns do not contain null or empty values.
    """
    def __init__(self, columns: list):
        self.columns = columns

    def validate(self, df: DataFrame) -> DataFrame:
        # Check for nulls or blank strings
        condition = F.lit(True)
        for col in self.columns:
            condition = condition & F.col(col).isNotNull() & (F.trim(F.col(col)) != "")
        
        rule_name = f"is_valid_null_check_{'_'.join(self.columns)[:30]}"
        return df.withColumn(rule_name, condition)

class QuantityRangeRule(ValidationRule):
    """
    Validation Rule: Quantity must be non-zero.
    Quantity can only be negative for cancellations (InvoiceNo starting with 'C').
    Quantity = 0 is always rejected.
    """
    def validate(self, df: DataFrame) -> DataFrame:
        # Quantity must not be 0.
        # If it's negative, InvoiceNo must start with 'C' (cancellation)
        condition = (F.col("Quantity") != 0) & (
            (F.col("Quantity") > 0) | 
            ((F.col("Quantity") < 0) & F.col("InvoiceNo").startswith("C"))
        )
        return df.withColumn("is_valid_quantity_range", condition)

class UnitPriceRangeRule(ValidationRule):
    """
    Validation Rule: UnitPrice must be non-negative (>= 0).
    """
    def validate(self, df: DataFrame) -> DataFrame:
        condition = F.col("UnitPrice") >= 0
        return df.withColumn("is_valid_unit_price_range", condition)

class InvoiceDateWindowRule(ValidationRule):
    """
    Validation Rule: InvoiceDate must fall within the known operating window
    (December 1, 2009 to December 31, 2011).
    """
    def __init__(self, start_date: str = "2009-12-01 00:00:00", end_date: str = "2011-12-31 23:59:59"):
        self.start_date = start_date
        self.end_date = end_date

    def validate(self, df: DataFrame) -> DataFrame:
        # Convert string timestamps for comparison
        condition = (
            (F.col("InvoiceDate") >= F.to_timestamp(F.lit(self.start_date))) & 
            (F.col("InvoiceDate") <= F.to_timestamp(F.lit(self.end_date)))
        )
        return df.withColumn("is_valid_invoice_date_window", condition)
