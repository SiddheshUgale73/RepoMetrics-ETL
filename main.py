import os 
import signal
import sys
import logging
import json
import config
from pipeline.client import GitHubClient, GitHubAPIError
from normalize_data import normalize_to_csv

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ETL_Orchestrator")

def run_pipeline():
    """
    Main ETL Orchestrator:
    - Extract: Fetch raw data from GitHub API with checkpointing.
    - Transform/Load: Normalize JSON to CSV.
    """
    logger.info("=== Starting Production ETL Pipeline ===")
    
    all_data = []
    processed_usernames = set()

    # Load existing progress if any
    if os.path.exists(config.RAW_DATA_FILE):
        try:
            with open(config.RAW_DATA_FILE, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
                processed_usernames = {u['username'] for u in all_data}
                logger.info(f"Resuming from checkpoint: {len(processed_usernames)} users already processed.")
        except Exception as e:
            logger.warning(f"Failed to load checkpoint file: {e}. Starting fresh.")

    def save_and_normalize():
        """Helper to save current progress and generate CSVs."""
        if all_data:
            logger.info(f"Saving {len(all_data)} records to {config.RAW_DATA_FILE}...")
            with open(config.RAW_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=4, ensure_ascii=False)
            logger.info("Updating CSV files...")
            normalize_to_csv()

    # Handle graceful shutdown (Ctrl+C)
    def signal_handler(sig, frame):
        logger.warning("\nInterrupt received! Saving progress before exiting...")
        save_and_normalize()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        client = GitHubClient()
        
        # 1. Extraction Phase
        logger.info(f"Phase 1: Extracting users for query: {config.DEFAULT_USER_QUERY}")
        raw_users = client.search_users(config.DEFAULT_USER_QUERY)
        
        total_users = len(raw_users)
        
        for idx, user in enumerate(raw_users, 1):
            username = user['login']
            
            if username in processed_usernames:
                logger.info(f"[{idx}/{total_users}] Skipping already processed user: {username}")
                continue

            logger.info(f"[{idx}/{total_users}] Extracting data for: {username}")
            
            try:
                user_entry = {
                    "username": username,
                    "profile": client.get_structured_user_profile(username),
                    "repositories": []
                }
                
                repos = client.get_structured_user_repositories(username)
                for repo in repos:
                    repo_name = repo['repo_name']
                    logger.info(f"  - Extracted repo: {repo_name}")
                    repo["commits"] = client.get_structured_repository_commits(username, repo_name)
                    repo["pull_requests"] = client.get_structured_repository_pull_requests(username, repo_name)
                    user_entry["repositories"].append(repo)
                
                all_data.append(user_entry)
                processed_usernames.add(username)

                # Incremental Save after each user
                save_and_normalize()

            except Exception as e:
                logger.error(f"Failed to process user {username}: {e}. Skipping to next.")
                continue

        logger.info("=== Pipeline Completed Successfully ===")
        print("\nPipeline execution complete. See logs/CSVs for details.")

    except GitHubAPIError as e:
        logger.critical(f"Pipeline failed due to API error: {e}")
    except Exception as e:
        logger.critical(f"An unexpected failure occurred: {e}", exc_info=True)

if __name__ == "__main__":
    run_pipeline()
