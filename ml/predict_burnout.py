"""
Burnout Detection Model: Student Fatigue Predictor

SPECIFICATION REFERENCE: TECHNICAL_SPEC.md § 1.2.1 (Burnout Detection Model)
TEST SPECIFICATION: TEST_SPEC.md § 1.4, § 2.2-A (Model Output & Integration Tests)

Algorithm: Isolation Forest (Unsupervised Anomaly Detection)
Contamination Rate: 5% (identifies top behavioral outliers)

Input Data Contract:
  - COMMITS: 146,333 rows with SHA, COMMIT_DATE, AUTHOR_ID
  - AUTHORS: 15,661 rows with ID, NAME
  
Feature Engineering (per § 1.2.1):
  - is_weekend: Commits on Sat(5) or Sun(6)
  - is_late_night: Commits between 10 PM - 4 AM
  - weekend_ratio: weekend_commits / total_commits (0.0-1.0)
  - late_night_ratio: late_night_commits / total_commits (0.0-1.0)
  - commits_per_day: total_commits / active_days

Output Data Contract:
  - Authors with >10 commits only (core contributors filter)
  - fatigue_score: -1 (anomaly/burnout risk), 1 (normal)
  - needs_mentor_attention: Boolean flag for flagged students

Expected Results (Validation per TEST_SPEC.md § 3.2-A):
  - ~89 flagged students (±10%) out of 1783 core developers
  
Artifacts Generated:
  - ml/burnout_model.joblib (trained model for reuse)
  - ml/student_fatigue_report.csv (high-risk students list)
"""

import os
import sys
import logging
import pandas as pd
import sqlite3
from sklearn.ensemble import IsolationForest
import joblib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("StudentActivityPredictor")

def get_sqlite_connection():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'repo_metrics.db')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    return sqlite3.connect(db_path)

def extract_commit_data(conn):
    """Extract commit history from SQLite to calculate developer activity patterns."""
    logger.info("Extracting Commits and Authors from SQLite...")
    query = """
        SELECT
            c.SHA,
            c.COMMIT_DATE,
            a.NAME as AUTHOR_NAME
        FROM COMMITS c
        JOIN AUTHORS a ON c.AUTHOR_ID = a.ID
    """
    df = pd.read_sql_query(query, conn)
    logger.info(f"Extracted {len(df)} commits.")
    return df

def feature_engineering(df):
    """Convert raw commits into developer-level behavioral features."""
    logger.info("Engineering student fatigue risk features...")
    
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
    
    # Features indicative of overwork / student fatigue
    X = features_df[['weekend_ratio', 'late_night_ratio', 'commits_per_day']]
    
    # We assume roughly 5% of top contributors are at high burnout risk
    model = IsolationForest(contamination=0.05, random_state=42)
    
    # Fit and Predict (-1 for anomaly/burnout risk, 1 for normal)
    predictions = model.fit_predict(X)
    
    features_df['fatigue_score'] = predictions
    # Convert to boolean flag for mentors
    features_df['needs_mentor_attention'] = features_df['fatigue_score'] == -1
    
    # Output some insights
    risk_count = features_df['needs_mentor_attention'].sum()
    logger.info(f"Model Training Complete. Identified {risk_count} students needing mentor check-ins.")
    
    return model, features_df

def main():
    logger.info("=== Starting Student Fatigue Predictor Pipeline ===")
    conn = None
    try:
        conn = get_sqlite_connection()

        # 1. Extract
        raw_df = extract_commit_data(conn)

        if raw_df.empty:
            logger.error("No commit data found in SQLite. Pipeline aborted.")
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
        csv_path = os.path.join(os.path.dirname(__file__), 'student_fatigue_report.csv')
        high_risk_devs = results_df[results_df['needs_mentor_attention'] == True]
        high_risk_devs.to_csv(csv_path, index=False)
        logger.info(f"\u2705 Saved Student Attention report to {csv_path}")

    except Exception as e:
        logger.critical(f"Pipeline Failed: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
