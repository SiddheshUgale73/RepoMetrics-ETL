import sqlite3
import pandas as pd
import os

def verify():
    conn = sqlite3.connect('repo_metrics.db')
    cursor = conn.cursor()
    
    tables = ['USER_TYPES', 'USERS', 'LANGUAGES', 'REPOSITORIES', 'AUTHORS', 'COMMITS', 'PULL_REQUESTS']
    csv_mapping = {
        'USER_TYPES': 'user_types.csv',
        'USERS': 'users.csv',
        'LANGUAGES': 'languages.csv',
        'REPOSITORIES': 'repositories.csv',
        'AUTHORS': 'authors.csv',
        'COMMITS': 'commits.csv',
        'PULL_REQUESTS': 'pull_requests.csv'
    }
    
    print("--- SQLite Verification ---")
    for table in tables:
        # DB count
        db_count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        
        # CSV count
        csv_file = csv_mapping[table]
        if os.path.exists(csv_file):
            csv_count = len(pd.read_csv(csv_file))
            status = "✅ MATCH" if db_count == csv_count else "❌ MISMATCH"
            print(f"{table:15} | DB: {db_count:7} | CSV: {csv_count:7} | {status}")
        else:
            print(f"{table:15} | DB: {db_count:7} | CSV: N/A")
            
    # Sample Join Query
    print("\n--- Sample Query (Top 5 Users by Public Repos) ---")
    query = """
    SELECT u.LOGIN, u.PUBLIC_REPOS, ut.TYPE_NAME
    FROM USERS u
    JOIN USER_TYPES ut ON u.TYPE_ID = ut.ID
    ORDER BY u.PUBLIC_REPOS DESC
    LIMIT 5
    """
    df = pd.read_sql_query(query, conn)
    print(df)
    
    conn.close()

if __name__ == "__main__":
    verify()
