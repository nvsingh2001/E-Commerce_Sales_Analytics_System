import os
import sys
from dotenv import load_dotenv
from platform_commands import (
    DatabaseConnector,
    RunETLCommand,
    GenerateChartsCommand,
    LaunchDashboardCommand,
    CheckStatsCommand,
)
from platform_ui import PlatformControlCenter


def main():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)

    db_connector = DatabaseConnector()

    commands = {
        "etl": RunETLCommand(db_connector),
        "charts": GenerateChartsCommand(db_connector),
        "dashboard": LaunchDashboardCommand(),
        "stats": CheckStatsCommand(db_connector),
    }

    control_center = PlatformControlCenter(db_connector, commands)
    control_center.parse_and_run(sys.argv[1:])


if __name__ == "__main__":
    main()
