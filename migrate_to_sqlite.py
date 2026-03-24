import sqlite3
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_NAME = "repo_metrics.db"
SCHEMA_FILE = "repo_metrics_schema.sql"

TABLES_TO_LOAD = [
    ("USER_TYPES", "user_types.csv"),
    ("USERS", "users.csv"),
    ("LANGUAGES", "languages.csv"),
    ("REPOSITORIES", "repositories.csv"),
    ("AUTHORS", "authors.csv"),
    ("COMMITS", "commits.csv"),
    ("PULL_REQUESTS", "pull_requests.csv")
]

def migrate():
    """Migrates CSV data to SQLite database."""
    if not os.path.exists(SCHEMA_FILE):
        logger.error(f"Schema file {SCHEMA_FILE} not found.")
        return

    try:
        # Connect to SQLite
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Create tables from schema
        logger.info(f"Creating tables from {SCHEMA_FILE}...")
        with open(SCHEMA_FILE, 'r') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)
        conn.commit()

        # Load CSVs
        for table_name, csv_file in TABLES_TO_LOAD:
            if not os.path.exists(csv_file):
                logger.warning(f"File {csv_file} not found. Skipping {table_name}.")
                continue

            logger.info(f"Loading {csv_file} into {table_name}...")
            # Using pandas for easy CSV loading and SQL insertion
            df = pd.read_csv(csv_file)
            
            # Special handling for potentially nested or empty data if needed
            # For now, simple to_sql should work as columns match
            df.to_sql(table_name, conn, if_exists='append', index=False)
            
            count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table_name}", conn)['count'][0]
            logger.info(f"Successfully loaded {table_name}. Row count: {count}")

        conn.close()
        logger.info("Migration to SQLite completed successfully.")

    except Exception as e:
        logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
