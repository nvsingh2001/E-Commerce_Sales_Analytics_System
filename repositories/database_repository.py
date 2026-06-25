from pyspark.sql import SparkSession, DataFrame
from config.settings import Settings


class DatabaseRepository:
    """
    Implements the Repository Pattern to isolate SQL/PostgreSQL database
    interactions (reads and writes) from PySpark execution logic.
    """

    def __init__(self, spark: SparkSession):
        self.spark = spark

        self.db_host = Settings.DB_HOST or "localhost"
        self.db_port = Settings.DB_PORT or "5432"
        self.db_name = Settings.DB_NAME or "ecommerce_db"
        self.db_user = Settings.DB_USER or "postgres"
        self.db_pass = Settings.DB_PASSWORD or "postgres"

        self.jdbc_url = (
            f"jdbc:postgresql://{self.db_host}:{self.db_port}/{self.db_name}"
        )
        self.jdbc_properties = {
            "user": self.db_user,
            "password": self.db_pass,
            "driver": "org.postgresql.Driver",
        }

    def truncate_all_tables(self) -> None:
        """
        Safely truncates all target database tables in the correct dependency order
        using a direct psycopg2 connection to avoid foreign key reference errors.
        """
        import psycopg2
        query = """
        TRUNCATE TABLE 
            fact_orders, 
            dim_customers, 
            dim_products, 
            analytics.revenue_summary, 
            analytics.customer_retention, 
            analytics.product_performance 
        RESTART IDENTITY CASCADE;
        """
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass
            )
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(query)
            cursor.close()
            conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to truncate database tables prior to load: {e}")

    def load_table(self, df: DataFrame, table_name: str) -> None:
        """
        Loads a PySpark DataFrame into a target PostgreSQL table using JDBC.
        Uses append mode since tables are pre-truncated.
        """
        try:
            df.write.format("jdbc").option("url", self.jdbc_url).option(
                "dbtable", table_name
            ).option("user", self.db_user).option("password", self.db_pass).option(
                "driver", self.jdbc_properties["driver"]
            ).mode("append").save()
        except Exception as e:
            raise RuntimeError(f"Failed to load table '{table_name}' via JDBC: {e}")

    def read_table(self, table_name: str) -> DataFrame:
        """
        Reads a PostgreSQL table into a PySpark DataFrame using JDBC.
        Useful for retrieving generated surrogate keys for fact table mapping.
        """
        try:
            return (
                self.spark.read.format("jdbc")
                .option("url", self.jdbc_url)
                .option("dbtable", table_name)
                .option("user", self.db_user)
                .option("password", self.db_pass)
                .option("driver", self.jdbc_properties["driver"])
                .load()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to read table '{table_name}' via JDBC: {e}")
