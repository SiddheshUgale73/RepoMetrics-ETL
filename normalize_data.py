import os
import json
import csv
import logging
from typing import List, Dict, Any
import config

# Configure logging for normalization
logger = logging.getLogger(__name__)

def normalize_to_csv():
    """
    Reads nested GitHub JSON data and flattens it into 7 normalized CSV files.
    - user_types.csv
    - users.csv
    - languages.csv
    - repositories.csv
    - authors.csv
    - commits.csv
    - pull_requests.csv
    """
    if not os.path.exists(config.RAW_DATA_FILE):
        logger.error(f"Source file {config.RAW_DATA_FILE} not found.")
        return

    logger.info(f"Starting complex data normalization from {config.RAW_DATA_FILE}...")

    with open(config.RAW_DATA_FILE, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    # Tables for storage
    user_types = {} # name -> id
    users = []
    languages = {} # name -> id
    repositories = []
    authors = {} # name -> id
    commits = []
    prs = []

    # Seen sets to avoid duplicates
    seen_users = set()
    seen_repos = set()
    seen_commits = set()
    seen_prs = set()

    def get_id(mapping, name):
        if not name: return None
        if name not in mapping:
            mapping[name] = len(mapping) + 1
        return mapping[name]

    for user_entry in all_data:
        profile = user_entry.get("profile", {})
        user_id = profile.get("id")

        if user_id and user_id not in seen_users:
            user_type_name = profile.get("type", "User")
            type_id = get_id(user_types, user_type_name)
            
            user_record = {
                "id": user_id,
                "login": profile.get("login"),
                "name": profile.get("name"),
                "type_id": type_id,
                "public_repos": profile.get("public_repos"),
                "followers": profile.get("followers"),
                "following": profile.get("following"),
                "created_at": profile.get("created_at")
            }
            users.append(user_record)
            seen_users.add(user_id)

        for repo in user_entry.get("repositories", []):
            repo_id = repo.get("repo_id")
            
            if repo_id and repo_id not in seen_repos:
                lang_name = repo.get("language")
                lang_id = get_id(languages, lang_name)
                
                repo_record = {
                    "id": repo_id,
                    "name": repo.get("repo_name"),
                    "language_id": lang_id,
                    "stargazers_count": repo.get("stargazers_count"),
                    "forks_count": repo.get("forks_count"),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "owner_id": user_id
                }
                repositories.append(repo_record)
                seen_repos.add(repo_id)

                for commit in repo.get("commits", []):
                    sha = commit.get("commit_sha")
                    if sha and (repo_id, sha) not in seen_commits:
                        author_name = commit.get("author_name")
                        author_id = get_id(authors, author_name)
                        
                        commits.append({
                            "sha": sha,
                            "repository_id": repo_id,
                            "author_id": author_id,
                            "commit_date": commit.get("commit_date")
                        })
                        seen_commits.add((repo_id, sha))
                
                for pr in repo.get("pull_requests", []):
                    pr_id = pr.get("pr_id")
                    if pr_id and pr_id not in seen_prs:
                        prs.append({
                            "pr_id": pr_id,
                            "repository_id": repo_id,
                            "pr_number": pr.get("pr_number"),
                            "title": pr.get("title"),
                            "state": pr.get("state"),
                            "author_login": pr.get("author_login"),
                            "created_at": pr.get("created_at"),
                            "merged_at": pr.get("merged_at")
                        })
                        seen_prs.add(pr_id)

    # Save to CSVs
    _save_list_to_csv([{"id": v, "type_name": k} for k, v in user_types.items()], config.USER_TYPES_CSV_FILE)
    _save_list_to_csv(users, config.USERS_CSV_FILE)
    _save_list_to_csv([{"id": v, "name": k} for k, v in languages.items()], config.LANGUAGES_CSV_FILE)
    _save_list_to_csv(repositories, config.REPOS_CSV_FILE)
    _save_list_to_csv([{"id": v, "name": k} for k, v in authors.items()], config.AUTHORS_CSV_FILE)
    _save_list_to_csv(commits, config.COMMITS_CSV_FILE)
    _save_list_to_csv(prs, config.PRS_CSV_FILE)

    logger.info("Complex normalization complete. 7 CSV files generated.")

def _save_list_to_csv(data_list: List[Dict[str, Any]], filename: str):
    """Utility to save a list of dictionaries to a CSV file."""
    if not data_list:
        logger.warning(f"No data to save for {filename}.")
        return

    # Extract headers from the first item
    headers = data_list[0].keys()

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data_list)
        logger.info(f"Successfully saved {len(data_list)} records to {filename}")
    except Exception as e:
        logger.error(f"Failed to save {filename}: {e}")

if __name__ == "__main__":
    # If run standalone, configure basic logging
    logging.basicConfig(level=logging.INFO)
    normalize_to_csv()
