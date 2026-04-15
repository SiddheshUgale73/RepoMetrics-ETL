import os
import sys
import logging
import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SubmissionPredictor")

def get_sqlite_connection():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'repo_metrics.db')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    return sqlite3.connect(db_path)

def extract_pr_data(conn):
    logger.info("Extracting submission history from SQLite...")
    # Only pull merged PRs to train the predictive model
    query = """
        SELECT
            PR_NUMBER,
            TITLE,
            CREATED_AT,
            MERGED_AT,
            AUTHOR_LOGIN,
            REPOSITORY_ID
        FROM PULL_REQUESTS
        WHERE STATE = 'closed' AND MERGED_AT IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    logger.info(f"Extracted {len(df)} merged Pull Requests.")
    return df

def feature_engineering(df):
    logger.info("Extracting features (Title Length, Creation Hour, Days to Merge)...")
    
    df['CREATED_AT'] = pd.to_datetime(df['CREATED_AT'], utc=True)
    df['MERGED_AT'] = pd.to_datetime(df['MERGED_AT'], utc=True)
    
    # Target Variable: Days to review
    df['days_to_review'] = (df['MERGED_AT'] - df['CREATED_AT']).dt.total_seconds() / (24 * 3600)
    
    # Filter out bizarrely long (e.g. 5 year) PRs which are outliers
    df = df[df['days_to_review'] < 365] 
    df = df[df['days_to_review'] > 0] 

    # Predictors: 
    df['title_length'] = df['TITLE'].str.len().fillna(0)
    df['created_hour'] = df['CREATED_AT'].dt.hour
    df['created_day_of_week'] = df['CREATED_AT'].dt.dayofweek
    
    # For now, simplistic author experience proxy: Number of PRs they have submitted 
    # (Since we only extracted historical PRs, this calculates how many past PRs they made)
    author_pr_counts = df.groupby('AUTHOR_LOGIN').cumcount()
    df['author_experience'] = author_pr_counts
    
    return df

def train_pr_model(df):
    logger.info("Training Random Forest Regressor to predict submission review duration...")
    features = ['title_length', 'created_hour', 'created_day_of_week', 'author_experience']
    
    X = df[features].fillna(0)
    y = df['days_to_review']
    
    # Needs at least some PRs to train
    if len(X) < 10:
        logger.warning("Not enough merged PR data in Snowflake to reliably train model.")
        return None, None
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    logger.info(f"Model Training Complete. Mean Absolute Error: {mae:.2f} Days")
    
    return model, df

def main():
    logger.info("=== Starting Student Submission Predictor ===")
    conn = None
    try:
        conn = get_sqlite_connection()
        raw_df = extract_pr_data(conn)

        if raw_df.empty:
            logger.error("No valid PR data found. Aborting.")
            return

        features_df = feature_engineering(raw_df)
        model, data = train_pr_model(features_df)

        if model:
            model_path = os.path.join(os.path.dirname(__file__), 'pr_bottleneck_model.joblib')
            joblib.dump(model, model_path)
            logger.info(f"\u2705 Saved model to {model_path}")
            
    except Exception as e:
        logger.critical(f"Pipeline Failed: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
