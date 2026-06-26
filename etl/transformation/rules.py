from abc import ABC, abstractmethod
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from config.settings import Settings


class ValidationRule(ABC):
    @abstractmethod
    def validate(self, df: DataFrame) -> DataFrame:
        pass


class NullCheckRule(ValidationRule):
    def __init__(self, columns: list):
        self.columns = columns

    def validate(self, df: DataFrame) -> DataFrame:
        condition = F.lit(True)
        for col in self.columns:
            condition = condition & F.col(col).isNotNull() & (F.trim(F.col(col)) != "")

        rule_name = f"is_valid_null_check_{'_'.join(self.columns)[:30]}"
        return df.withColumn(rule_name, condition)


class QuantityRangeRule(ValidationRule):
    def __init__(self, quantity_col: str = "quantity", invoice_col: str = "invoice_no"):
        self.quantity_col = quantity_col
        self.invoice_col = invoice_col

    def validate(self, df: DataFrame) -> DataFrame:
        condition = (F.col(self.quantity_col) != 0) & (
            (F.col(self.quantity_col) > 0)
            | ((F.col(self.quantity_col) < 0) & F.col(self.invoice_col).startswith("C"))
        )
        return df.withColumn("is_valid_quantity_range", condition)


class UnitPriceRangeRule(ValidationRule):
    def __init__(self, unit_price_col: str = "unit_price"):
        self.unit_price_col = unit_price_col

    def validate(self, df: DataFrame) -> DataFrame:
        condition = F.col(self.unit_price_col) >= 0
        return df.withColumn("is_valid_unit_price_range", condition)


class InvoiceDateWindowRule(ValidationRule):
    def __init__(
        self,
        start_date: str = Settings.DATASET_START_DATE,
        end_date: str = Settings.DATASET_END_DATE,
        date_col: str = "order_date",
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.date_col = date_col

    def validate(self, df: DataFrame) -> DataFrame:
        condition = (
            F.col(self.date_col) >= F.to_timestamp(F.lit(self.start_date))
        ) & (F.col(self.date_col) <= F.to_timestamp(F.lit(self.end_date)))
        return df.withColumn("is_valid_invoice_date_window", condition)
