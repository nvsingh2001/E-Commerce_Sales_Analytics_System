import os
import sys
import subprocess
import argparse
import psycopg2
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)


def print_banner():
    banner = """
====================================================================
 🛍️  E-COMMERCE SALES ANALYTICS SYSTEM - PLATFORM CONTROL CENTER
====================================================================
    """
    print(banner)


def get_db_connection():
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT", "5432")

    if not all([db_host, db_name, db_user, db_pass]):
        return None

    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_pass,
            connect_timeout=5,
        )
        return conn
    except Exception:
        return None


def check_system_stats():
    print("\n🔍 Checking Database Health & System Statistics...")
    conn = get_db_connection()
    if conn is None:
        print("❌ Database Status: OFFLINE (Could not connect to AWS RDS PostgreSQL)")
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

    # Query summary metrics
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


def run_etl_pipeline():
    print("\n🚀 Starting PySpark ETL Pipeline Stage...")
    print("Initializing Spark session and loading datasets...")
    try:
        # Import dynamically to avoid heavy PySpark overhead if not running ETL
        from etl.pipeline import EcommerceSalesAnalyticsPipeline

        pipeline = EcommerceSalesAnalyticsPipeline()
        pipeline.run()
        print("\n✅ PySpark ETL Pipeline execution completed successfully!")
    except Exception as e:
        print(f"\n❌ PySpark ETL Pipeline failed: {e}")


def run_static_charts():
    print("\n🎨 Generating Static Charts (Matplotlib/Seaborn)...")
    try:
        from visualizations.generate_charts import main as generate_main

        generate_main()
        print(
            "\n✅ All static charts regenerated successfully in 'visualizations/static/'!"
        )
    except Exception as e:
        print(f"\n❌ Static chart generation failed: {e}")


def run_streamlit_dashboard():
    print("\n🖥️ Starting Streamlit Interactive Dashboard Server...")
    print("Dashboard will load at: http://localhost:8501")
    try:
        # Run streamlit as a subprocess
        subprocess.run(
            [".venv/bin/streamlit", "run", "visualizations/dashboard_app.py"]
        )
    except KeyboardInterrupt:
        print("\nStreamlit server stopped.")
    except Exception as e:
        print(f"\n❌ Failed to launch Streamlit: {e}")


def interactive_menu():
    while True:
        print_banner()
        print("Please choose an operation:")
        print("  1. Run End-to-End PySpark ETL Pipeline (Extract -> Clean -> Load)")
        print("  2. Regenerate Static Charts (Matplotlib & Seaborn)")
        print("  3. Launch Streamlit Interactive Dashboard (Web UI)")
        print("  4. View Database Health & Statistics")
        print("  5. Run Full Analytics Suite (Pipeline + Regenerate Charts)")
        print("  6. Exit")
        print("-" * 60)

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            run_etl_pipeline()
        elif choice == "2":
            run_static_charts()
        elif choice == "3":
            run_streamlit_dashboard()
        elif choice == "4":
            check_system_stats()
        elif choice == "5":
            run_etl_pipeline()
            run_static_charts()
        elif choice == "6":
            print("\nExiting Platform Control Center. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 6.")

        input("\nPress Enter to return to the menu...")


def main():
    parser = argparse.ArgumentParser(
        description="E-Commerce Sales Analytics Platform CLI Manager"
    )
    parser.add_argument(
        "--etl", action="store_true", help="Run the end-to-end PySpark ETL pipeline"
    )
    parser.add_argument(
        "--charts",
        action="store_true",
        help="Regenerate static Seaborn/Matplotlib charts",
    )
    parser.add_argument(
        "--dashboard", action="store_true", help="Start the Streamlit dashboard server"
    )
    parser.add_argument(
        "--stats", action="store_true", help="View RDS database row counts and metrics"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run ETL pipeline and regenerate static charts",
    )

    args = parser.parse_args()

    # If no CLI args are provided, fall back to interactive menu
    if not any(vars(args).values()):
        interactive_menu()
    else:
        print_banner()
        if args.stats:
            check_system_stats()
        if args.etl or args.all:
            run_etl_pipeline()
        if args.charts or args.all:
            run_static_charts()
        if args.dashboard:
            run_streamlit_dashboard()


if __name__ == "__main__":
    main()
