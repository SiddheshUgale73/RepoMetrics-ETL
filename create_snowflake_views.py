import os
import snowflake.connector
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Snowflake_View_Creator")

def create_views():
    sf_user = os.getenv('SNOWFLAKE_USER')
    sf_password = os.getenv('SNOWFLAKE_PASSWORD')
    sf_account = os.getenv('SNOWFLAKE_ACCOUNT')
    sf_warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
    sf_database = os.getenv('SNOWFLAKE_DATABASE', 'GITSTAR_DB')
    sf_schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')

    if not all([sf_user, sf_password, sf_account]):
        logger.error("Missing Snowflake credentials in .env file.")
        return

    logger.info(f"Connecting to Snowflake account: {sf_account}...")
    
    try:
        conn = snowflake.connector.connect(
            user=sf_user,
            password=sf_password,
            account=sf_account,
            warehouse=sf_warehouse,
            database=sf_database,
            schema=sf_schema
        )
        
        cursor = conn.cursor()
        
        logger.info("Reading power_bi_views.sql...")
        with open('power_bi_views.sql', 'r') as f:
            sql_queries = f.read().split(';')
            
        for query in sql_queries:
            if query.strip():
                logger.info(f"Executing: {query.strip()[:50]}...")
                cursor.execute(query)
                
        logger.info("✅ All Dashboard Views created successfully in Snowflake.")
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to create Snowflake views: {e}")

if __name__ == "__main__":
    create_views()
