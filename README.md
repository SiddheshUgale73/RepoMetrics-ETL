# GitStar Analytics: Enterprise GitHub-to-Snowflake Pipeline

A high-performance Data Engineering pipeline designed to extract massive datasets from the GitHub API, normalize them into a relational schema, and stage them for Cloud Data Warehousing in **Snowflake**.

## 🚀 Overview
This project evolves a simple data scraper into a production-grade ETL (Extract, Transform, Load) engine. It is capable of handling hundreds of thousands of records (commits, PRs, repos) and organizing them into a complex 7-table normalized schema optimized for modern analytics.

## 🏗 Architecture & Workflow

### 1. Data Extraction (Python)
The `main.py` orchestrator performs a deep-crawl of the GitHub API.
- **Resumable ETL**: Automatically resumes from the last processed user if interrupted.
- **Incremental Saving**: Saves progress after every user to prevent data loss.
- **Rich Data Scope**: Extracts Profiles, Repositories, Commits (limit 100/repo), and Pull Requests (limit 50/repo).

### 2. Complex Normalization (7 Tables)
The `normalize_data.py` script transforms nested JSON into a relational structure ready for **Snowflake**.
- **Schema**:
  - `USER_TYPES`: Categorizes accounts (User vs Organization).
  - `USERS`: Detailed contributor profiles.
  - `LANGUAGES`: Unique programming languages across all repos.
  - `REPOSITORIES`: Metadata for 12,000+ repositories.
  - `AUTHORS`: Unique Git authors across 500k+ commits.
  - `COMMITS`: Transactional commit history.
  - `PULL_REQUESTS`: Full lifecycle tracking (Open/Closed/Merged).

### 3. Snowflake Integration
The project includes a ready-to-use **`snowflake_ddl.sql`** script to set up your cloud data warehouse in seconds.

## 🛠 Setup & Usage

### Prerequisites
- Python 3.8+
- GitHub Personal Access Token (PAT)
- Snowflake Account

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure your `.env` file:
   ```env
   GITHUB_TOKEN=your_token_here
   ```

### Running the Pipeline
1. **Extract Raw Data**:
   ```bash
   python main.py
   ```
2. **Normalize for Snowflake**:
   ```bash
   python normalize_data.py
   ```
3. **Load to Snowflake**:
   - Run the SQL in `snowflake_ddl.sql` in your Snowflake worksheet.
   - Use the Snowflake Web UI or SnowSQL to upload the generated CSV files.

## 📁 Project Structure
- `main.py`: The ETL Orchestrator.
- `normalize_data.py`: The Transformation Engine.
- `pipeline/`: Core GitHub API client package.
- `snowflake_ddl.sql`: Snowflake table definitions.
- `config.py`: Global settings and file paths.

---
**Build your strong analytics engine with GitStar Analytics!**
