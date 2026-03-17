import os
import logging
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Snowflake_Loader")

def get_snowflake_connection():
    """Establish a connection to Snowflake."""
    sf_user = os.getenv('SNOWFLAKE_USER')
    sf_password = os.getenv('SNOWFLAKE_PASSWORD')
    sf_account = os.getenv('SNOWFLAKE_ACCOUNT')
    sf_warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
    sf_database = os.getenv('SNOWFLAKE_DATABASE', 'GITSTAR_DB')
    sf_schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')

    if not all([sf_user, sf_password, sf_account]):
        raise ValueError("Missing Snowflake credentials in .env file (USER, PASSWORD, or ACCOUNT).")

    logger.info(f"Connecting to Snowflake account: {sf_account}...")
    
    # We use Snowflake connector to connect to base account, without specifying DB if it doesn't exist yet
    # Or, assuming the DB and schema exist or will be created
    conn = snowflake.connector.connect(
        user=sf_user,
        password=sf_password,
        account=sf_account,
        warehouse=sf_warehouse,
        # Remove DB and Schema initially in case they need to be created first
    )
    
    # Let's ensure Database and Schema exist
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {sf_database}")
    cursor.execute(f"USE DATABASE {sf_database}")
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {sf_schema}")
    cursor.execute(f"USE SCHEMA {sf_schema}")
    
    return conn

def setup_tables(conn):
    """Execute the DDL script to create all necessary tables."""
    logger.info("Setting up Snowflake tables from snowflake_ddl.sql...")
    try:
        with open('snowflake_ddl.sql', 'r') as f:
            sql_queries = f.read().split(';')
            
        cursor = conn.cursor()
        for query in sql_queries:
            if query.strip():
                cursor.execute(query)
        logger.info("✅ All tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to setup database tables: {e}")
        raise

def load_csv_data(conn):
    """Upload CSVs to internal stages and COPY INTO tables."""
    # Loading order matters for Foreign Keys! (Parents -> Children)
    tables_to_load = [
        ("USER_TYPES", "user_types.csv"),
        ("USERS", "users.csv"),
        ("LANGUAGES", "languages.csv"),
        ("REPOSITORIES", "repositories.csv"),
        ("AUTHORS", "authors.csv"),
        ("COMMITS", "commits.csv"),
        ("PULL_REQUESTS", "pull_requests.csv")
    ]
    
    cursor = conn.cursor()
    
    for table_name, csv_filename in tables_to_load:
        if not os.path.exists(csv_filename):
            logger.warning(f"⚠️ File '{csv_filename}' not found! Skipping '{table_name}'.")
            continue
            
        logger.info(f"Loading '{csv_filename}' into '{table_name}'...")
        
        try:
            # 1. Pushing the CSV file to the Table's internal stage (@%table_name)
            # Use forward slashes for cross-platform compatibility in the PUT command
            file_path = csv_filename.replace('\\', '/')
            put_query = f"PUT file://{os.path.abspath(file_path)} @%{table_name} auto_compress=true overwrite=true"
            cursor.execute(put_query)
            
            # 2. Copy the data from the stage into the table
            copy_query = f"""
                COPY INTO {table_name}
                FROM @%{table_name}
                FILE_FORMAT = (TYPE = CSV, FIELD_OPTIONALLY_ENCLOSED_BY = '"', SKIP_HEADER = 1)
                ON_ERROR = 'CONTINUE'
            """
            cursor.execute(copy_query)
            
            # 3. Verify total rows loaded
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            logger.info(f"✅ Successfully loaded {table_name}. Total rows in table: {count}\n")
            
        except snowflake.connector.errors.ProgrammingError as e:
            logger.error(f"❌ Snowflake Error on {table_name}: {e}")
        except Exception as e:
            logger.error(f"❌ Error loading {table_name}: {e}")

def main():
    logger.info("=== Starting Automated Snowflake Loader ===")
    conn = None
    try:
        conn = get_snowflake_connection()
        setup_tables(conn)
        load_csv_data(conn)
        logger.info("=== Snowflake Loading Completed Successfully ===")
    except ValueError as e:
        logger.error(str(e))
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logger.info("Snowflake connection closed safely.")

if __name__ == "__main__":
    main()
