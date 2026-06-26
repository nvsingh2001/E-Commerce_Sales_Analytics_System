import sys
from repositories.database_connector import DatabaseConnector
from platform_commands import (
    RunETLCommand,
    GenerateChartsCommand,
    LaunchDashboardCommand,
    CheckStatsCommand,
)
from platform_ui import PlatformControlCenter


def main():
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
