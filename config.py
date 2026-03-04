import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Retry Settings
RETRY_COUNT = 3
RETRY_BACKOFF_FACTOR = 1
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

# Rate Limit Settings
PROACTIVE_RATE_LIMIT_THRESHOLD = 10  # Wait if remaining requests are below this

# File Paths
RAW_DATA_FILE = "github_raw_data.json"
USERS_CSV_FILE = "users.csv"
USER_TYPES_CSV_FILE = "user_types.csv"
REPOS_CSV_FILE = "repositories.csv"
LANGUAGES_CSV_FILE = "languages.csv"
COMMITS_CSV_FILE = "commits.csv"
AUTHORS_CSV_FILE = "authors.csv"
PRS_CSV_FILE = "pull_requests.csv"
LOG_FILE = "pipeline.log"

# Search Settings
DEFAULT_USER_LIMIT = 50
DEFAULT_USER_QUERY = "repos:>5 followers:>5"
DEFAULT_PER_PAGE = 50
COMMIT_LIMIT_PER_REPO = 100
PR_LIMIT_PER_REPO = 50
