import os
import sys
import logging
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RepoHealth")

def get_snowflake_connection():
    sf_user = os.getenv('SNOWFLAKE_USER')
    sf_password = os.getenv('SNOWFLAKE_PASSWORD')
    sf_account = os.getenv('SNOWFLAKE_ACCOUNT')
    return snowflake.connector.connect(
        user=sf_user, password=sf_password, account=sf_account,
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
        database=os.getenv('SNOWFLAKE_DATABASE', 'GITSTAR_DB'),
        schema=os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
    )

def extract_repo_health_data(conn):
    logger.info("Extracting Repo data to gauge maintenance health...")
    # Get repositories and aggregate commit data directly in SQL
    query = """
        SELECT 
            r.ID,
            r.NAME,
            r.STARGAZERS_COUNT,
            COUNT(c.SHA) as TOTAL_COMMITS,
            COUNT(DISTINCT c.AUTHOR_ID) as UNIQUE_CONTRIBUTORS,
            MAX(c.COMMIT_DATE) as LAST_COMMIT_DATE
        FROM REPOSITORIES r
        LEFT JOIN COMMITS c ON r.ID = c.REPOSITORY_ID
        GROUP BY r.ID, r.NAME, r.STARGAZERS_COUNT
    """
    cursor = conn.cursor()
    cursor.execute(query)
    df = cursor.fetch_pandas_all()
    logger.info(f"Extracted health indicators for {len(df)} templates.")
    return df

def feature_engineering(df):
    logger.info("Engineering Repo Health Metrics...")
    
    # Fill NAs for repos with 0 commits
    df['TOTAL_COMMITS'] = df['TOTAL_COMMITS'].fillna(0)
    df['UNIQUE_CONTRIBUTORS'] = df['UNIQUE_CONTRIBUTORS'].fillna(0)
    
    # Days since last commit (abandonment risk)
    df['LAST_COMMIT_DATE'] = pd.to_datetime(df['LAST_COMMIT_DATE'], utc=True)
    now = pd.Timestamp.now(tz='UTC')
    df['days_since_active'] = (now - df['LAST_COMMIT_DATE']).dt.days
    
    # Max out at 5 years to handle NaNs/Super old repos
    df['days_since_active'] = df['days_since_active'].fillna(1800)
    
    # Bus factor proxy (Stars vs Contributors vs Commits)
    # A repo with 1 contributor and many commits is high risk (Low Bus Factor)
    
    # Filter to actual repos worth grading
    df = df[df['TOTAL_COMMITS'] > 0]
    return df

def cluster_repos(df):
    logger.info("Using K-Means Clustering to Grade Repositories (A to F)...")
    
    features = ['STARGAZERS_COUNT', 'TOTAL_COMMITS', 'UNIQUE_CONTRIBUTORS', 'days_since_active']
    X = df[features]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # We want 4 classes: A(Healthy), B(Maintained), C(At Risk), F(Abandoned)
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    df['health_cluster'] = clusters
    
    # We map clusters to grades based on "days_since_active" centroids
    # The cluster with the highest avg days_since_active gets 'F', lowest gets 'A'
    cluster_health = df.groupby('health_cluster')['days_since_active'].mean().sort_values()
    
    grade_map = {
        cluster_health.index[0]: 'A (Very Healthy)',
        cluster_health.index[1]: 'B (Maintained)',
        cluster_health.index[2]: 'C (At Risk)',
        cluster_health.index[3]: 'D/F (Abandoned/Deprecated)'
    }
    
    df['health_grade'] = df['health_cluster'].map(grade_map)
    
    logger.info("Clustering Complete. Sample spread:")
    logger.info(df['health_grade'].value_counts())
    
    return kmeans, scaler, df

def main():
    logger.info("=== Starting Repo Health Scorer ===")
    conn = None
    try:
        conn = get_snowflake_connection()
        raw_df = extract_repo_health_data(conn)
        
        if raw_df.empty:
            logger.error("No valid Repository data found. Aborting.")
            return

        features_df = feature_engineering(raw_df)
        model, scaler, results_df = cluster_repos(features_df)
        
        model_path = os.path.join(os.path.dirname(__file__), 'repo_health_model.joblib')
        joblib.dump({'model': model, 'scaler': scaler}, model_path)
        
        # Save rankings to CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'repo_health_rankings.csv')
        results_df[['NAME', 'STARGAZERS_COUNT', 'health_grade', 'days_since_active']].sort_values('days_since_active').to_csv(csv_path, index=False)
        logger.info(f"\u2705 Saved Model to {model_path}")
        logger.info(f"\u2705 Saved Repo Rankings to {csv_path}")
            
    except Exception as e:
        logger.critical(f"Pipeline Failed: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
