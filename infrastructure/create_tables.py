from repositories.database_connector import DatabaseConnector
from utils.sql_loader import SQLLoader


class SchemaInitializer:
    def __init__(self, db_connector: DatabaseConnector):
        self._db_connector = db_connector

    def initialize_schema(self) -> None:
        conn = self._db_connector.get_connection()
        if conn is None:
            raise ConnectionError("Failed to connect to the database.")
        try:
            sql_script = SQLLoader.load_schema("create_tables.sql")
            print("Executing SQL schema script...")
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(sql_script)
            cursor.close()
            print("Database schema and tables created successfully!")
        except Exception as e:
            raise RuntimeError(f"Error initializing database schema: {e}")
        finally:
            conn.close()


def main():
    db_connector = DatabaseConnector()
    initializer = SchemaInitializer(db_connector)
    initializer.initialize_schema()


if __name__ == "__main__":
    main()
