import os


class SQLLoader:
    """Shared utility for loading SQL query files from the sql/ directory."""

    _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def load_query(filename: str, subdirectory: str = "analysis_queries") -> str:
        """Reads and returns the contents of a SQL file."""
        sql_path = os.path.join(
            SQLLoader._project_root, "sql", subdirectory, filename
        )
        with open(sql_path, "r") as f:
            return f.read()

    @staticmethod
    def load_schema(filename: str) -> str:
        """Reads and returns the contents of a SQL schema file."""
        return SQLLoader.load_query(filename, subdirectory="schema")
