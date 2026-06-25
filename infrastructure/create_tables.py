import os
import psycopg2
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "ecommerce_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD")
    
    print(f"Connecting to database {db_name} on {db_host}...")
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        sql_path = "sql/schema/create_tables.sql"
        print(f"Reading SQL schema from {sql_path}...")
        with open(sql_path, "r") as f:
            sql_script = f.read()
            
        print("Executing SQL script...")
        cursor.execute(sql_script)
        print("Database schema and tables created successfully!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error initializing database schema: {e}")
        exit(1)

if __name__ == "__main__":
    main()
