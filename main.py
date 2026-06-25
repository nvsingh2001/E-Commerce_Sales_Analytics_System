import os
import sys
import subprocess
import argparse
import psycopg2
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)


class DatabaseConnector:
    """
    Encapsulates database credentials and connection logic, shielding client code
    from database-specific configurations.
    """
    def __init__(self):
        self._db_host = os.getenv('DB_HOST')
        self._db_name = os.getenv('DB_NAME')
        self._db_user = os.getenv('DB_USER')
        self._db_pass = os.getenv('DB_PASSWORD')
        self._db_port = os.getenv('DB_PORT', '5432')

    def get_connection(self):
        """Creates and returns a psycopg2 database connection."""
        if not all([self._db_host, self._db_name, self._db_user, self._db_pass]):
            return None
        try:
            return psycopg2.connect(
                host=self._db_host,
                port=self._db_port,
                database=self._db_name,
                user=self._db_user,
                password=self._db_pass,
                connect_timeout=5
            )
        except Exception:
            return None


class PlatformCommand(ABC):
    """
    Abstract interface for all platform tasks (Command Pattern).
    Declares the single execution interface 'execute'.
    """
    @abstractmethod
    def execute(self) -> None:
        """Executes the specific platform command."""
        pass


class RunETLCommand(PlatformCommand):
    """
    Encapsulates the execution of the PySpark ETL Pipeline.
    """
    def execute(self) -> None:
        print("\n🚀 Starting PySpark ETL Pipeline Stage...")
        print("Initializing Spark session and loading datasets...")
        try:
            # Dynamic import to minimize PySpark loading latency when not running ETL
            from etl.pipeline import EcommerceSalesAnalyticsPipeline
            pipeline = EcommerceSalesAnalyticsPipeline()
            pipeline.run()
            print("\n✅ PySpark ETL Pipeline execution completed successfully!")
        except Exception as e:
            print(f"\n❌ PySpark ETL Pipeline failed: {e}")


class GenerateChartsCommand(PlatformCommand):
    """
    Encapsulates the generation of static analytical report charts.
    """
    def execute(self) -> None:
        print("\n🎨 Generating Static Charts (Matplotlib/Seaborn)...")
        try:
            from visualizations.generate_charts import main as generate_main
            generate_main()
            print("\n✅ All static charts regenerated successfully in 'visualizations/static/'!")
        except Exception as e:
            print(f"\n❌ Static chart generation failed: {e}")


class LaunchDashboardCommand(PlatformCommand):
    """
    Encapsulates spinning up the Streamlit interactive dashboard.
    """
    def execute(self) -> None:
        print("\n🖥️ Starting Streamlit Interactive Dashboard Server...")
        print("Dashboard will load at: http://localhost:8501")
        try:
            subprocess.run([".venv/bin/streamlit", "run", "visualizations/dashboard_app.py"])
        except KeyboardInterrupt:
            print("\nStreamlit server stopped.")
        except Exception as e:
            print(f"\n❌ Failed to launch Streamlit: {e}")


class CheckStatsCommand(PlatformCommand):
    """
    Queries and displays database health and system statistics (row counts).
    """
    def __init__(self, db_connector: DatabaseConnector):
        self._db_connector = db_connector

    def execute(self) -> None:
        print("\n🔍 Checking Database Health & System Statistics...")
        conn = self._db_connector.get_connection()
        if conn is None:
            print("❌ Database Status: OFFLINE (Could not connect to AWS RDS PostgreSQL)")
            return
            
        print("✅ Database Status: ONLINE (Connected to AWS RDS PostgreSQL)")
        cur = conn.cursor()
        
        tables = [
            ('dim_customers', 'Dimension - Customers'),
            ('dim_products', 'Dimension - Products'),
            ('fact_orders', 'Fact - Orders'),
            ('analytics.revenue_summary', 'Reporting - Revenue Summary'),
            ('analytics.customer_retention', 'Reporting - Customer Retention'),
            ('analytics.product_performance', 'Reporting - Product Performance')
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
            cur.execute("SELECT SUM(line_total) FROM fact_orders WHERE order_status = 'Completed'")
            total_rev = cur.fetchone()[0] or 0.0
            cur.execute("SELECT COUNT(DISTINCT order_id) FROM fact_orders WHERE order_status = 'Completed'")
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


class PlatformControlCenter:
    """
    Coordinates platform command execution. It uses dependency injection
    to execute subclasses of PlatformCommand.
    """
    def __init__(self, db_connector: DatabaseConnector):
        self._db_connector = db_connector
        
        # Instantiate commands (Open/Closed Principle: easily extendable with new commands)
        self._commands = {
            'etl': RunETLCommand(),
            'charts': GenerateChartsCommand(),
            'dashboard': LaunchDashboardCommand(),
            'stats': CheckStatsCommand(self._db_connector)
        }

    def print_banner(self) -> None:
        banner = """
====================================================================
 🛍️  E-COMMERCE SALES ANALYTICS SYSTEM - PLATFORM CONTROL CENTER
====================================================================
        """
        print(banner)

    def execute_command(self, cmd_key: str) -> None:
        """Executes a command by its key."""
        command = self._commands.get(cmd_key)
        if command:
            command.execute()
        else:
            print(f"❌ Command key '{cmd_key}' is not recognized.")

    def run_interactive_menu(self) -> None:
        """Launches the CLI interactive console selection menu."""
        while True:
            self.print_banner()
            print("Please choose an operation:")
            print("  1. Run End-to-End PySpark ETL Pipeline (Extract -> Clean -> Load)")
            print("  2. Regenerate Static Charts (Matplotlib & Seaborn)")
            print("  3. Launch Streamlit Interactive Dashboard (Web UI)")
            print("  4. View Database Health & Statistics")
            print("  5. Run Full Analytics Suite (Pipeline + Regenerate Charts)")
            print("  6. Exit")
            print("-" * 60)
            
            choice = input("Enter choice (1-6): ").strip()
            
            if choice == '1':
                self.execute_command('etl')
            elif choice == '2':
                self.execute_command('charts')
            elif choice == '3':
                self.execute_command('dashboard')
            elif choice == '4':
                self.execute_command('stats')
            elif choice == '5':
                self.execute_command('etl')
                self.execute_command('charts')
            elif choice == '6':
                print("\nExiting Platform Control Center. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please enter a number between 1 and 6.")
            
            input("\nPress Enter to return to the menu...")


def main():
    parser = argparse.ArgumentParser(description="E-Commerce Sales Analytics Platform CLI Manager")
    parser.add_argument('--etl', action='store_true', help='Run the end-to-end PySpark ETL pipeline')
    parser.add_argument('--charts', action='store_true', help='Regenerate static Seaborn/Matplotlib charts')
    parser.add_argument('--dashboard', action='store_true', help='Start the Streamlit dashboard server')
    parser.add_argument('--stats', action='store_true', help='View RDS database row counts and metrics')
    parser.add_argument('--all', action='store_true', help='Run ETL pipeline and regenerate static charts')
    
    args = parser.parse_args()
    
    # Instantiate Connector and Control Center
    db_connector = DatabaseConnector()
    control_center = PlatformControlCenter(db_connector)
    
    # Check flags
    if not any(vars(args).values()):
        control_center.run_interactive_menu()
    else:
        control_center.print_banner()
        if args.stats:
            control_center.execute_command('stats')
        if args.etl or args.all:
            control_center.execute_command('etl')
        if args.charts or args.all:
            control_center.execute_command('charts')
        if args.dashboard:
            control_center.execute_command('dashboard')


if __name__ == '__main__':
    main()
