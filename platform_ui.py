import sys
import argparse
from repositories.database_connector import DatabaseConnector
from platform_commands import PlatformCommand


class PlatformControlCenter:
    def __init__(self, db_connector: DatabaseConnector, commands: dict):
        self._db_connector = db_connector
        self._commands = commands

    def get_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="BridgeLabz E-Commerce Sales Analytics Platform - Control Center"
        )
        parser.add_argument(
            "action",
            choices=list(self._commands.keys()),
            help="The platform action to perform (etl, charts, dashboard, stats)",
        )
        return parser

    def check_db_health(self) -> bool:
        print("Checking target database health...")
        conn = self._db_connector.get_connection()
        if conn is None:
            print(
                "CRITICAL: Failed to connect to the AWS RDS database. Is the instance running?"
            )
            return False
        conn.close()
        print("Database connection verified.")
        return True

    def parse_and_run(self, args: list) -> None:
        parser = self.get_parser()
        if not args:
            parser.print_help()
            sys.exit(1)

        parsed_args = parser.parse_args(args)
        action = parsed_args.action

        if action not in self._commands:
            print(f"Error: Unknown action '{action}'")
            parser.print_help()
            sys.exit(1)

        if not self.check_db_health():
            sys.exit(1)

        command: PlatformCommand = self._commands[action]
        try:
            command.execute()
        except Exception as e:
            print(f"\nPlatform Execution Failed during '{action}': {e}")
            sys.exit(1)
