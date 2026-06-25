import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repositories.database_connector import DatabaseConnector


class SchemaInitializer:
    """
    Manages the initialization and recreation of the database schema tables.
    Adheres to dependency injection by accepting the DatabaseConnector.
    """

    def __init__(
        self,
        db_connector: DatabaseConnector,
        sql_path: str = "sql/schema/create_tables.sql",
    ):
        self._db_connector = db_connector
        self._sql_path = sql_path

    def initialize_schema(self) -> None:
        """Reads the SQL schema script and executes it against the database."""
        conn = self._db_connector.get_connection()
        if conn is None:
            print(
                "❌ Failed to connect to the database. Schema initialization aborted."
            )
            sys.exit(1)

        print(f"Reading SQL schema script from: {self._sql_path}...")
        try:
            with open(self._sql_path, "r") as f:
                sql_script = f.read()

            print("Executing SQL schema script...")
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(sql_script)
            cursor.close()
            conn.close()
            print("✅ Database schema and tables created successfully!")
        except Exception as e:
            print(f"❌ Error initializing database schema: {e}")
            if conn:
                conn.close()
            sys.exit(1)


def main():
    load_dotenv()

    db_connector = DatabaseConnector()
    initializer = SchemaInitializer(db_connector)
    initializer.initialize_schema()


if __name__ == "__main__":
    main()
