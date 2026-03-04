# GitHub Data Extraction Pipeline

A Python project for searching GitHub users and extracting their profile information, repositories, and commits.

## Features
- **GitHub API Integration**: Uses the `requests` library.
- **Search API**: Find users based on search queries.
- **Profiling**: Fetch detailed profile data for discovered users.
- **Repository Listing**: List all public repositories for a user.
- **Commit History**: Retrieve commit history for specific repositories.
- **Pagination Handling**: Automatically handles paginated responses from the GitHub API.
- **Rate Limit Handling**: Detects rate limits and waits (sleeps) until they reset.
- **Error Handling**: Gracefully handles API errors and network issues.

## Setup

1. **Clone or Download** the project.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   - Rename `.env.example` to `.env`.
   - Update `GITHUB_TOKEN` in the `.env` file with your GitHub Personal Access Token.
     [Create a token here](https://github.com/settings/tokens).

## Usage

Run the extraction pipeline:
```bash
python main.py <username-query>
```
Example:
```bash
python main.py "octocat"
```

## Structure
- `pipeline/client.py`: Core `GitHubClient` class for API interactions.
- `main.py`: Entry point for searching and extracting data.
- `.env`: (Private) Stores your GitHub token.
