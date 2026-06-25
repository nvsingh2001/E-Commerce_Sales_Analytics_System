import sys
import argparse
from repositories.database_connector import DatabaseConnector
from platform_commands import PlatformCommand


class PlatformControlCenter:
    """
    Coordinates and handles the platform UI layers (CLI arguments and console menu loops).
    Adheres to the Single Responsibility Principle (SRP) by delegating execution to injected commands.
    """

    def __init__(self, db_connector: DatabaseConnector, commands: dict):
        self._db_connector = db_connector
        self._commands = commands

    def print_banner(self) -> None:
        """Prints the system header banner."""
        banner = """
====================================================================
 🛍️  E-COMMERCE SALES ANALYTICS SYSTEM - PLATFORM CONTROL CENTER
====================================================================
        """
        print(banner)

    def execute_command(self, cmd_key: str) -> None:
        """Retrieves and executes a command strategy from the injected command list."""
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

            if choice == "1":
                self.execute_command("etl")
            elif choice == "2":
                self.execute_command("charts")
            elif choice == "3":
                self.execute_command("dashboard")
            elif choice == "4":
                self.execute_command("stats")
            elif choice == "5":
                self.execute_command("etl")
                self.execute_command("charts")
            elif choice == "6":
                print("\nExiting Platform Control Center. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please enter a number between 1 and 6.")

            input("\nPress Enter to return to the menu...")

    def parse_and_run(self, args_list: list) -> None:
        """Parses Command Line Arguments and executes matched tasks."""
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
            "--dashboard",
            action="store_true",
            help="Start the Streamlit dashboard server",
        )
        parser.add_argument(
            "--stats",
            action="store_true",
            help="View RDS database row counts and metrics",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Run ETL pipeline and regenerate static charts",
        )

        args = parser.parse_args(args_list)

        # If no arguments are provided, launch the interactive menu loop
        if not any(vars(args).values()):
            self.run_interactive_menu()
        else:
            self.print_banner()
            if args.stats:
                self.execute_command("stats")
            if args.etl or args.all:
                self.execute_command("etl")
            if args.charts or args.all:
                self.execute_command("charts")
            if args.dashboard:
                self.execute_command("dashboard")
