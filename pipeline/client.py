import os
import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any, Dict, List, Optional
import config

# Configure logging for the client
logger = logging.getLogger(__name__)

class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub client with retry strategy and proactive rate limiting.
        """
        self.token = token or config.GITHUB_TOKEN
        if not self.token:
            raise GitHubAPIError("GITHUB_TOKEN not found in environment or config")
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Setup retry strategy
        retry_strategy = Retry(
            total=config.RETRY_COUNT,
            backoff_factor=config.RETRY_BACKOFF_FACTOR,
            status_forcelist=config.RETRY_STATUS_CODES,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update(self.headers)

    def _check_rate_limit(self, response: requests.Response):
        """Proactively check rate limits and wait if necessary."""
        remaining = int(response.headers.get("X-RateLimit-Remaining", 100))
        reset_time = int(response.headers.get("X-RateLimit-Reset", time.time()))
        
        if remaining < config.PROACTIVE_RATE_LIMIT_THRESHOLD:
            wait_time = max(reset_time - int(time.time()), 0) + 1
            logger.warning(f"Proactive rate limit hit (Remaining: {remaining}). Waiting {wait_time}s...")
            time.sleep(wait_time)

    def _handle_error_response(self, response: requests.Response):
        """Centralized error handling for API responses."""
        if response.status_code == 403 and "X-RateLimit-Reset" in response.headers:
            reset_time = int(response.headers["X-RateLimit-Reset"])
            wait_time = max(reset_time - int(time.time()), 0) + 1
            logger.error(f"Rate limit exceeded. Waiting {wait_time}s...")
            time.sleep(wait_time)
            return True # Signal to retry (though Session/Retry handles some, we handle 403 manually)
        
        if response.status_code == 409 and "empty" in response.text.lower():
            logger.warning(f"Repository is empty (409). Skipping data fetch.")
            return "EMPTY"

        if response.status_code != 200:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            raise GitHubAPIError(f"API request failed with status {response.status_code}")
        
        return False

    def _request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Authenticated request with retry and rate limit handling."""
        while True:
            try:
                resp = self.session.get(url, params=params)
                self._check_rate_limit(resp)
                
                error_signal = self._handle_error_response(resp)
                if error_signal == True:
                    continue
                if error_signal == "EMPTY":
                    return {} # Return empty dict for single object request
                    
                return resp.json()
            except requests.RequestException as e:
                logger.error(f"Network error: {e}")
                raise GitHubAPIError(f"HTTP request failed: {e}")

    def _paginated_request(self, url: str, params: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> List[Any]:
        """Handle pagination with proactive rate limiting and optional limit."""
        results = []
        current_url = url
        current_params = params

        while current_url:
            try:
                resp = self.session.get(current_url, params=current_params)
                self._check_rate_limit(resp)
                
                error_signal = self._handle_error_response(resp)
                if error_signal == True:
                    continue
                if error_signal == "EMPTY":
                    return [] # Return empty list for paginated request

                data = resp.json()
                items = []
                if isinstance(data, list):
                    items = data
                elif "items" in data:
                    items = data["items"]
                else:
                    items = [data]

                results.extend(items)

                if limit and len(results) >= limit:
                    logger.info(f"Limit of {limit} reached for {url}")
                    return results[:limit]

                # Pagination
                link_header = resp.headers.get("Link")
                current_url = None
                if link_header:
                    for part in link_header.split(", "):
                        if 'rel="next"' in part:
                            current_url = part[part.find("<") + 1 : part.find(">")]
                            current_params = None
                            break
            except requests.RequestException as e:
                logger.error(f"Network error during pagination: {e}")
                raise GitHubAPIError(f"HTTP request failed: {e}")

        return results

    def search_users(self, query: str, per_page: int = config.DEFAULT_PER_PAGE, limit: Optional[int] = config.DEFAULT_USER_LIMIT) -> List[Dict[str, Any]]:
        url = f"{config.GITHUB_API_BASE_URL}/search/users"
        params = {"q": query, "per_page": per_page}
        logger.info(f"Searching users with query: {query}")
        return self._paginated_request(url, params, limit=limit)

    def get_user_profile(self, username: str) -> Dict[str, Any]:
        url = f"{config.GITHUB_API_BASE_URL}/users/{username}"
        logger.info(f"Fetching profile for: {username}")
        return self._request(url)

    def get_user_repositories(self, username: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        url = f"{config.GITHUB_API_BASE_URL}/users/{username}/repos"
        logger.info(f"Fetching repositories for: {username}")
        return self._paginated_request(url, limit=limit)

    def get_repository_commits(self, username: str, repo_name: str, limit: Optional[int] = config.COMMIT_LIMIT_PER_REPO) -> List[Dict[str, Any]]:
        url = f"{config.GITHUB_API_BASE_URL}/repos/{username}/{repo_name}/commits"
        logger.info(f"Fetching commits for: {username}/{repo_name}")
        return self._paginated_request(url, limit=limit)

    def get_structured_user_profile(self, username: str) -> Dict[str, Any]:
        raw_profile = self.get_user_profile(username)
        fields = ['id', 'login', 'name', 'public_repos', 'followers', 'following', 'created_at']
        return {field: raw_profile.get(field) for field in fields}

    def get_structured_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        url = f"{config.GITHUB_API_BASE_URL}/users/{username}/repos"
        params = {"per_page": 100}
        raw_repos = self._paginated_request(url, params)
        
        fields_map = {
            'id': 'repo_id',
            'name': 'repo_name',
            'language': 'language',
            'stargazers_count': 'stargazers_count',
            'forks_count': 'forks_count',
            'created_at': 'created_at',
            'updated_at': 'updated_at'
        }
        
        structured_repos = []
        for repo in raw_repos:
            structured_repo = {new_key: repo.get(old_key) for old_key, new_key in fields_map.items()}
            structured_repos.append(structured_repo)
            
        return structured_repos

    def get_structured_repository_commits(self, username: str, repo_name: str, limit: int = config.COMMIT_LIMIT_PER_REPO) -> List[Dict[str, Any]]:
        url = f"{config.GITHUB_API_BASE_URL}/repos/{username}/{repo_name}/commits"
        params = {"per_page": 100 if limit >= 100 else limit}
        raw_commits = self._paginated_request(url, params, limit=limit)
        
        structured_commits = []
        for commit in raw_commits:
            commit_data = commit.get('commit', {})
            author = commit_data.get('author', {})
            
            structured_commits.append({
                'commit_sha': commit.get('sha'),
                'author_name': author.get('name'),
                'commit_date': author.get('date')
            })
            
        return structured_commits
    def get_repository_pull_requests(self, username: str, repo_name: str, limit: Optional[int] = config.PR_LIMIT_PER_REPO) -> List[Dict[str, Any]]:
        url = f"{config.GITHUB_API_BASE_URL}/repos/{username}/{repo_name}/pulls"
        params = {"state": "all"} # Fetch both open and closed PRs
        logger.info(f"Fetching pull requests for: {username}/{repo_name}")
        return self._paginated_request(url, params, limit=limit)

    def get_structured_repository_pull_requests(self, username: str, repo_name: str, limit: int = config.PR_LIMIT_PER_REPO) -> List[Dict[str, Any]]:
        raw_prs = self.get_repository_pull_requests(username, repo_name, limit=limit)
        
        structured_prs = []
        for pr in raw_prs:
            user = pr.get('user', {})
            structured_prs.append({
                'pr_id': pr.get('id'),
                'pr_number': pr.get('number'),
                'title': pr.get('title'),
                'state': pr.get('state'),
                'author_login': user.get('login'),
                'created_at': pr.get('created_at'),
                'closed_at': pr.get('closed_at'),
                'merged_at': pr.get('merged_at')
            })
            
        return structured_prs
