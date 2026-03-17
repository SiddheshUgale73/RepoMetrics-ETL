import os
import sys
import logging
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from sklearn.ensemble import IsolationForest
import joblib

# Load environment variables
# We need to look in the parent directory for .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BurnoutPredictor")

def get_snowflake_connection():
    sf_user = os.getenv('SNOWFLAKE_USER')
    sf_password = os.getenv('SNOWFLAKE_PASSWORD')
    sf_account = os.getenv('SNOWFLAKE_ACCOUNT')
    sf_warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
    sf_database = os.getenv('SNOWFLAKE_DATABASE', 'GITSTAR_DB')
    sf_schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')

    if not all([sf_user, sf_password, sf_account]):
        raise ValueError("Missing Snowflake credentials in .env file.")

    return snowflake.connector.connect(
        user=sf_user,
        password=sf_password,
        account=sf_account,
        warehouse=sf_warehouse,
        database=sf_database,
        schema=sf_schema
    )

def extract_commit_data(conn):
    """Extract commit history from Snowflake to calculate developer activity patterns."""
    logger.info("Extracting Commits and Authors from Snowflake...")
    query = """
        SELECT 
            c.SHA,
            c.COMMIT_DATE,
            a.NAME as AUTHOR_NAME
        FROM COMMITS c
        JOIN AUTHORS a ON c.AUTHOR_ID = a.ID
    """
    cursor = conn.cursor()
    cursor.execute(query)
    # Fetch as pandas DataFrame
    df = cursor.fetch_pandas_all()
    logger.info(f"Extracted {len(df)} commits.")
    return df

def feature_engineering(df):
    """Convert raw commits into developer-level behavioral features."""
    logger.info("Engineering burnout risk features...")
    
    # Ensure datetime format
    df['COMMIT_DATE'] = pd.to_datetime(df['COMMIT_DATE'], utc=True)
    
    # Extract temporal features
    df['day_of_week'] = df['COMMIT_DATE'].dt.dayofweek # 0=Mon, 6=Sun
    df['hour_of_day'] = df['COMMIT_DATE'].dt.hour
    
    # Define risky behaviors
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    # Late night: 10 PM to 4 AM
    df['is_late_night'] = ((df['hour_of_day'] >= 22) | (df['hour_of_day'] <= 4)).astype(int)

    # Aggregate by Author
    author_stats = df.groupby('AUTHOR_NAME').agg(
        total_commits=('SHA', 'count'),
        weekend_commits=('is_weekend', 'sum'),
        late_night_commits=('is_late_night', 'sum'),
        first_commit=('COMMIT_DATE', 'min'),
        last_commit=('COMMIT_DATE', 'max')
    ).reset_index()

    # Filter out inactive/one-off committers to focus on core team
    author_stats = author_stats[author_stats['total_commits'] > 10]
    
    # Calculate ratios
    author_stats['weekend_ratio'] = author_stats['weekend_commits'] / author_stats['total_commits']
    author_stats['late_night_ratio'] = author_stats['late_night_commits'] / author_stats['total_commits']
    
    # Calculate commit density (commits per active day)
    author_stats['active_days'] = (author_stats['last_commit'] - author_stats['first_commit']).dt.days
    # Avoid division by zero
    author_stats['active_days'] = author_stats['active_days'].apply(lambda x: x if x > 0 else 1)
    author_stats['commits_per_day'] = author_stats['total_commits'] / author_stats['active_days']

    logger.info(f"Engineered features for {len(author_stats)} core developers.")
    return author_stats

def train_burnout_model(features_df):
    """Use Unsupervised Learning (Isolation Forest) to find overworked anomalies."""
    logger.info("Training Isolation Forest Anomaly Detector...")
    
    # Features indicative of overwork / burnout
    X = features_df[['weekend_ratio', 'late_night_ratio', 'commits_per_day']]
    
    # We assume roughly 5% of top contributors are at high burnout risk
    model = IsolationForest(contamination=0.05, random_state=42)
    
    # Fit and Predict (-1 for anomaly/burnout risk, 1 for normal)
    predictions = model.fit_predict(X)
    
    features_df['burnout_risk'] = predictions
    # Convert to boolean flag
    features_df['is_high_risk'] = features_df['burnout_risk'] == -1
    
    # Output some insights
    risk_count = features_df['is_high_risk'].sum()
    logger.info(f"Model Training Complete. Identified {risk_count} developers at high risk of burnout.")
    
    return model, features_df

def main():
    logger.info("=== Starting Developer Burnout Predictor Pipeline ===")
    conn = None
    try:
        conn = get_snowflake_connection()
        
        # 1. Extract
        raw_df = extract_commit_data(conn)
        
        if raw_df.empty:
            logger.error("No commit data found in Snowflake. Pipeline aborted.")
            return

        # 2. Transform
        author_features = feature_engineering(raw_df)
        
        # 3. Model
        model, results_df = train_burnout_model(author_features)
        
        # 4. Save Artifacts
        os.makedirs(os.path.dirname(__file__), exist_ok=True)
        model_path = os.path.join(os.path.dirname(__file__), 'burnout_model.joblib')
        joblib.dump(model, model_path)
        logger.info(f"\u2705 Saved trained model to {model_path}")
        
        # Save sample insights for review
        csv_path = os.path.join(os.path.dirname(__file__), 'burnout_risk_report.csv')
        high_risk_devs = results_df[results_df['is_high_risk'] == True]
        high_risk_devs.to_csv(csv_path, index=False)
        logger.info(f"\u2705 Saved High-Risk Developer report to {csv_path}")

    except Exception as e:
        logger.critical(f"Pipeline Failed: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
