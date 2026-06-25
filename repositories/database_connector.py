import os
import psycopg2
from config.settings import Settings

class DatabaseConnector:
    """
    Singleton Database Connector class. Ensures only a single connection 
    configuration instance is shared across the platform components.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
            cls._instance._db_host = Settings.DB_HOST
            cls._instance._db_name = Settings.DB_NAME
            cls._instance._db_user = Settings.DB_USER
            cls._instance._db_pass = Settings.DB_PASSWORD
            cls._instance._db_port = Settings.DB_PORT
        return cls._instance

    def get_connection(self):
        """Creates and returns a new psycopg2 connection instance based on the singleton config."""
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
