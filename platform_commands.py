import os
import subprocess
import shutil
from abc import ABC, abstractmethod
from repositories.database_connector import DatabaseConnector
from utils.sql_loader import SQLLoader
from config.settings import Settings


class PlatformCommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class RunETLCommand(PlatformCommand):
    def __init__(self, db_connector: DatabaseConnector):
        self._db_connector = db_connector

    def execute(self) -> None:
        from etl.pipeline import EcommerceSalesAnalyticsPipeline

        print("\nStarting the ETL Pipeline execution...")
        pipeline = EcommerceSalesAnalyticsPipeline()
        pipeline.run()
        print("ETL Pipeline completed successfully.")


class GenerateChartsCommand(PlatformCommand):
    def __init__(self, db_connector: DatabaseConnector):
        self._db_connector = db_connector

    def execute(self) -> None:
        from visualizations.generate_charts import main as generate_main

        print("\nGenerating static visualization charts...")
        generate_main()
        print("Charts generation completed. Check 'visualizations/static/'")


class LaunchDashboardCommand(PlatformCommand):
    def execute(self) -> None:
        print("\nLaunching Streamlit Interactive Dashboard...")
        streamlit_executable = shutil.which("streamlit") or ".venv/bin/streamlit"
        
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        
        subprocess.run(
            [streamlit_executable, "run", "visualizations/dashboard_app.py"],
            env=env
        )


class CheckStatsCommand(PlatformCommand):
    def __init__(self, db_connector: DatabaseConnector):
        self._db_connector = db_connector

    def execute(self) -> None:
        print("\nChecking Target Database Row Counts and Metrics...")

        conn = self._db_connector.get_connection()
        if conn is None:
            print("Failed to connect to the database to check stats.")
            return

        try:
            cursor = conn.cursor()
            print("\n--- Current Table Row Counts ---")

            for table_name, table_label in Settings.TABLE_LABELS.items():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"{table_label} ({table_name}): {count} rows")
                except Exception as e:
                    print(f"{table_label} ({table_name}): Error counting rows - {e}")
                    conn.rollback()

            print("\n--- High-Level Business Metrics ---")
            try:
                revenue_query = SQLLoader.load_query("total_revenue.sql")
                cursor.execute(revenue_query)
                total_rev = cursor.fetchone()[0] or 0.0
                print(f"Total Completed Revenue: £{total_rev:,.2f}")

                orders_query = SQLLoader.load_query("total_orders.sql")
                cursor.execute(orders_query)
                total_orders = cursor.fetchone()[0] or 0
                print(f"Total Completed Orders: {total_orders:,}")

            except Exception as e:
                print(f"Error computing business metrics: {e}")
                conn.rollback()

            cursor.close()
        except Exception as e:
            print(f"An unexpected error occurred while checking stats: {e}")
        finally:
            conn.close()
