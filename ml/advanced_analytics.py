import pandas as pd
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Advanced_Analytics")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..')
COMMITS_CSV = os.path.join(DATA_DIR, 'commits.csv')
REPOS_CSV = os.path.join(DATA_DIR, 'repositories.csv')
AUTHORS_CSV = os.path.join(DATA_DIR, 'authors.csv')
OUTPUT_CSV = os.path.join(BASE_DIR, 'advanced_insights.csv')

def calculate_bus_factor(commit_counts):
    """
    Number of contributors whose cumulative share of commits is > 50%.
    Simplified version of the Bus Factor.
    """
    total_commits = commit_counts.sum()
    if total_commits == 0:
        return 0
    
    sorted_counts = commit_counts.sort_values(ascending=False)
    cumulative_share = sorted_counts.cumsum() / total_commits
    
    # The number of people it takes to reach > 50%
    bus_factor = (cumulative_share <= 0.50).sum() + 1
    return bus_factor

def generate_insights():
    logger.info("Starting Advanced Analytics generation...")
    
    if not all(os.path.exists(f) for f in [COMMITS_CSV, REPOS_CSV, AUTHORS_CSV]):
        logger.error("Missing required CSV files.")
        return

    # Load data
    commits = pd.read_csv(COMMITS_CSV)
    repos = pd.read_csv(REPOS_CSV)
    authors = pd.read_csv(AUTHORS_CSV)
    
    # Convert dates
    commits['commit_date'] = pd.to_datetime(commits['commit_date'])
    
    insights = []
    
    for _, repo in repos.iterrows():
        repo_id = repo['id']
        repo_name = repo['name']
        
        repo_commits = commits[commits['repository_id'] == repo_id]
        
        if repo_commits.empty:
            insights.append({
                'REPO_ID': repo_id,
                'NAME': repo_name,
                'BUS_FACTOR': 0,
                'VELOCITY': 0,
                'STALENESS': (datetime.now() - pd.to_datetime(repo['updated_at']).tz_localize(None)).days,
                'TOP_CONTRIBUTOR_CONCENTRATION': 0,
                'ACTIVE_AUTHORS': 0
            })
            continue
            
        # 1. Bus Factor & Concentration
        author_commit_counts = repo_commits['author_id'].value_counts()
        bus_factor = calculate_bus_factor(author_commit_counts)
        top_contrib_pct = (author_commit_counts.iloc[0] / author_commit_counts.sum()) * 100 if not author_commit_counts.empty else 0
        
        # 2. Project Velocity (Commits per week)
        first_commit = repo_commits['commit_date'].min()
        last_commit = repo_commits['commit_date'].max()
        duration_weeks = (last_commit - first_commit).days / 7
        if duration_weeks < 1: duration_weeks = 1
        velocity = len(repo_commits) / duration_weeks
        
        # 3. Staleness (Days since last commit)
        staleness = (datetime.now().replace(tzinfo=None) - last_commit.replace(tzinfo=None)).days
        
        insights.append({
            'REPO_ID': repo_id,
            'NAME': repo_name,
            'BUS_FACTOR': bus_factor,
            'VELOCITY': round(velocity, 2),
            'STALENESS': staleness,
            'TOP_CONTRIBUTOR_CONCENTRATION': round(top_contrib_pct, 2),
            'ACTIVE_AUTHORS': len(author_commit_counts)
        })

    # Save to CSV
    df_insights = pd.DataFrame(insights)
    df_insights.to_csv(OUTPUT_CSV, index=False)
    logger.info(f"Advanced insights saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    generate_insights()
