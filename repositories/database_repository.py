from pyspark.sql import SparkSession, DataFrame
from config.settings import Settings
from repositories.database_connector import DatabaseConnector
from utils.sql_loader import SQLLoader


class DatabaseRepository:
    """Implements the Repository Pattern to isolate database interactions from PySpark logic."""

    def __init__(self, spark: SparkSession, db_connector: DatabaseConnector):
        self._spark = spark
        self._db_connector = db_connector
        self._jdbc_url = (
            f"jdbc:postgresql://{Settings.DB_HOST}:{Settings.DB_PORT}/{Settings.DB_NAME}"
        )
        self._jdbc_properties = {
            "user": Settings.DB_USER,
            "password": Settings.DB_PASSWORD,
            "driver": "org.postgresql.Driver",
        }

    def truncate_all_tables(self) -> None:
        """Truncates all target tables using the DatabaseConnector singleton."""
        conn = self._db_connector.get_connection()
        if conn is None:
            raise RuntimeError("Cannot truncate tables: database connection unavailable.")
        try:
            query = SQLLoader.load_schema("truncate_tables.sql")
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(query)
            cursor.close()
        finally:
            conn.close()

    def load_table(self, df: DataFrame, table_name: str) -> None:
        """Loads a PySpark DataFrame into a PostgreSQL table via JDBC."""
        try:
            (
                df.write.format("jdbc")
                .option("url", self._jdbc_url)
                .option("dbtable", table_name)
                .option("user", self._jdbc_properties["user"])
                .option("password", self._jdbc_properties["password"])
                .option("driver", self._jdbc_properties["driver"])
                .mode("append")
                .save()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load table '{table_name}' via JDBC: {e}")

    def read_table(self, table_name: str) -> DataFrame:
        """Reads a PostgreSQL table into a PySpark DataFrame via JDBC."""
        try:
            return (
                self._spark.read.format("jdbc")
                .option("url", self._jdbc_url)
                .option("dbtable", table_name)
                .option("user", self._jdbc_properties["user"])
                .option("password", self._jdbc_properties["password"])
                .option("driver", self._jdbc_properties["driver"])
                .load()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to read table '{table_name}' via JDBC: {e}")
