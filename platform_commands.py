import subprocess
from abc import ABC, abstractmethod
from repositories.database_connector import DatabaseConnector


class PlatformCommand(ABC):
    """
    Abstract Command Interface (Command Design Pattern).
    Defines the execute method.
    """

    @abstractmethod
    def execute(self) -> None:
        """Executes the specific platform command."""
        pass


class RunETLCommand(PlatformCommand):
    """
    Encapsulates PySpark ETL Pipeline execution.
    """

    def __init__(self, db_connector: DatabaseConnector):
        self._db_connector = db_connector

    def execute(self) -> None:
        print("\n🚀 Starting PySpark ETL Pipeline Stage...")
        print("Initializing Spark session and loading datasets...")
        try:
            # Dynamic import to avoid heavy Spark overhead at CLI startup
            from etl.pipeline import EcommerceSalesAnalyticsPipeline

            # Run the pipeline (which internally connects to PostgreSQL/S3)
            pipeline = EcommerceSalesAnalyticsPipeline()
            pipeline.run()
            print("\n✅ PySpark ETL Pipeline execution completed successfully!")
        except Exception as e:
            print(f"\n❌ PySpark ETL Pipeline failed: {e}")


class GenerateChartsCommand(PlatformCommand):
    """
    Encapsulates static chart generation strategy.
    """

    def __init__(self, db_connector: DatabaseConnector):
        self._db_connector = db_connector

    def execute(self) -> None:
        print("\n🎨 Generating Static Charts (Matplotlib/Seaborn)...")
        try:
            from visualizations.generate_charts import main as generate_main

            generate_main()
            print(
                "\n✅ All static charts regenerated successfully in 'visualizations/static/'!"
            )
        except Exception as e:
            print(f"\n❌ Static chart generation failed: {e}")


class LaunchDashboardCommand(PlatformCommand):
    """
    Encapsulates Streamlit interactive dashboard launch.
    """

    def execute(self) -> None:
        print("\n🖥️ Starting Streamlit Interactive Dashboard Server...")
        print("Dashboard will load at: http://localhost:8501")
        try:
            # Launch Streamlit as a subprocess using virtual environment binary
            subprocess.run(
                [".venv/bin/streamlit", "run", "visualizations/dashboard_app.py"]
            )
        except KeyboardInterrupt:
            print("\nStreamlit server stopped.")
        except Exception as e:
            print(f"\n❌ Failed to launch Streamlit: {e}")


class CheckStatsCommand(PlatformCommand):
    """
    Encapsulates checking of database table row counts and summary statistics.
    """

    def __init__(self, db_connector: DatabaseConnector):
        self._db_connector = db_connector

    def execute(self) -> None:
        print("\n🔍 Checking Database Health & System Statistics...")
        conn = self._db_connector.get_connection()
        if conn is None:
            print(
                "❌ Database Status: OFFLINE (Could not connect to AWS RDS PostgreSQL)"
            )
            return

        print("✅ Database Status: ONLINE (Connected to AWS RDS PostgreSQL)")
        cur = conn.cursor()

        tables = [
            ("dim_customers", "Dimension - Customers"),
            ("dim_products", "Dimension - Products"),
            ("fact_orders", "Fact - Orders"),
            ("analytics.revenue_summary", "Reporting - Revenue Summary"),
            ("analytics.customer_retention", "Reporting - Customer Retention"),
            ("analytics.product_performance", "Reporting - Product Performance"),
        ]

        print("\n📊 Current Database Row Counts:")
        print("-" * 60)
        for table_name, label in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cur.fetchone()[0]
                print(f"  • {label:<35} : {count:,} rows")
            except Exception as e:
                print(f"  • {label:<35} : Error reading table ({e})")
                conn.rollback()

        print("-" * 60)

        try:
            cur.execute(
                "SELECT SUM(line_total) FROM fact_orders WHERE order_status = 'Completed'"
            )
            total_rev = cur.fetchone()[0] or 0.0
            cur.execute(
                "SELECT COUNT(DISTINCT order_id) FROM fact_orders WHERE order_status = 'Completed'"
            )
            total_orders = cur.fetchone()[0] or 0
            aov = float(total_rev) / total_orders if total_orders > 0 else 0.0

            print(f"💡 Key Metrics in RDS:")
            print(f"  • Total Revenue      : £{float(total_rev):,.2f}")
            print(f"  • Total Orders       : {total_orders:,}")
            print(f"  • Avg Order Value    : £{aov:,.2f}")
        except Exception as e:
            conn.rollback()

        cur.close()
        conn.close()
        print("=" * 60)
