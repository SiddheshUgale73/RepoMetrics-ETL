# Technical Specification: GitHub Projects Insights

## 1. System Components & Specifications

### 1.1 Data Layer Specification

#### Database Schema Spec
**Component**: `repo_metrics.db` (SQLite)
**Location**: Root directory
**Initialization**: Via `repo_metrics_schema.sql`

**Tables**:
| Table | Primary Key | Purpose | Constraints |
|-------|-------------|---------|------------|
| USER_TYPES | ID (INT) | Categorize users (User/Organization) | NOT NULL |
| USERS | ID (INT) | GitHub user profiles | TYPE_ID FK required |
| LANGUAGES | ID (INT) | Programming languages | Unique names |
| REPOSITORIES | ID (INT) | Project repositories | OWNER_ID FK to USERS |
| AUTHORS | ID (INT) | Git commit authors | Unique names |
| COMMITS | SHA (TEXT), REPOSITORY_ID (INT) | Commit history | 146K+ expected rows |
| PULL_REQUESTS | PR_ID (INT) | Pull request lifecycle | REPOSITORY_ID FK required |

**Data Integrity Rules**:
- Foreign keys must be enforced (`PRAGMA foreign_keys = ON`)
- NULL handling: Optional fields default to NULL, mandatory fields reject NULL
- Date format: ISO 8601 (`YYYY-MM-DD HH:MM:SS`)

---

#### CSV to Database Migration Spec
**Component**: `migrate_to_sqlite.py`
**Input**: 7 CSV files (users.csv, commits.csv, etc.)
**Output**: Populated SQLite database
**Processing Steps**:
1. Load schema from SQL file
2. For each CSV: Sanitize data → Align columns → Batch insert
3. Verify row counts match source CSVs

**Data Sanitization Rules**:
- Trim whitespace from all string columns
- Convert NULL-like values ("NA", "N/A", "") to Python None
- Parse numeric columns (*_id, *_count, etc.) as integers
- Parse date columns (created_at, merged_at, etc.) as ISO 8601 strings
- Drop rows with no meaningful data (all NULLs)

**Error Handling**:
- File not found → Log warning, skip table
- Schema mismatch → Raise ValueError with details
- Insertion failure → Log error, attempt next batch
- Database exists → Recreate fresh copy on each run

**Success Criteria**:
- All 7 tables populated
- Row counts: USER_TYPES=1, USERS=21, LANGUAGES=70, REPOSITORIES=3320, AUTHORS=15661, COMMITS=146333, PULL_REQUESTS=29875
- Foreign key relationships intact

---

### 1.2 Machine Learning Pipeline Specification

#### 1.2.1 Burnout Detection Model
**Component**: `ml/predict_burnout.py`
**Algorithm**: Isolation Forest (Unsupervised Anomaly Detection)
**Contamination Rate**: 5% (assume ~5% of developers at burnout risk)

**Data Contract**:
```
Input: COMMITS table with SHA, COMMIT_DATE, AUTHOR_ID
       AUTHORS table with ID, NAME
Processing: Extract temporal patterns per author
Output: DataFrame with columns:
  - AUTHOR_NAME (str)
  - total_commits (int, > 10 minimum)
  - weekend_ratio (float, 0.0-1.0)
  - late_night_ratio (float, 0.0-1.0)
  - commits_per_day (float)
  - needs_mentor_attention (bool)
```

**Feature Engineering**:
- **is_weekend**: Commits on Saturday(5) or Sunday(6)
- **is_late_night**: Commits between 10 PM - 4 AM (hours 22-4)
- **weekend_ratio**: weekend_commits / total_commits
- **late_night_ratio**: late_night_commits / total_commits
- **commits_per_day**: total_commits / active_days (min 1 day)

**Model Behavior**:
- Filter: Only authors with >10 commits (core contributors)
- Anomalies: Marked as -1 by Isolation Forest
- Output flag: `needs_mentor_attention = (fatigue_score == -1)`

**Expected Results**:
- ~89 students flagged out of 1783 core developers
- Flagged students have abnormal weekend/late-night patterns

**Output Artifacts**:
- Model: `ml/burnout_model.joblib`
- Report: `ml/student_fatigue_report.csv` (high-risk developers)

**Error Handling**:
- Empty result set → Log error, skip model training
- Invalid dates → Coerce to NaT, filter out
- Database connection failure → Raise with context

---

#### 1.2.2 PR Merge Time Predictor
**Component**: `ml/predict_pr_merge.py`
**Algorithm**: Random Forest Regressor
**Target**: Days to merge a PR

**Data Contract**:
```
Input: PULL_REQUESTS where STATE='closed' AND MERGED_AT IS NOT NULL
Processing: Feature engineering on PR metadata
Output: Prediction model + MAE metric
```

**Features**:
- **title_length**: Character count of PR title
- **creation_hour**: Hour of day PR was created (0-23)
- **days_to_merge**: (MERGED_AT - CREATED_AT).days [TARGET]

**Model Performance**:
- Mean Absolute Error: ~11-12 days
- Train-test split: 80-20

**Expected Results**:
- 15,242 merged PRs analyzed
- Model accuracy within ±1 day error margin

**Output Artifacts**:
- Model: `ml/pr_bottleneck_model.joblib`
- Accessible for inference in dashboard

---

#### 1.2.3 Project Health Clustering
**Component**: `ml/repo_health_score.py`
**Algorithm**: K-Means (k=4 clusters, random_state=42)

**Data Contract**:
```
Input: REPOSITORIES with COMMITS aggregated
       Per repo: star_count, total_commits, unique_contributors, days_since_last_commit
Processing: Feature scaling → K-Means clustering
Output: Cluster assignments mapped to grades A-F
```

**Features**:
- **star_count**: STARGAZERS_COUNT
- **total_commits**: COUNT(COMMITS)
- **unique_contributors**: COUNT(DISTINCT AUTHOR_ID)
- **days_since_active**: Days since last commit

**Cluster Mapping**:
- Cluster 0 → A (Excellent Progress)
- Cluster 1 → B (Good Progress)
- Cluster 2 → C (Slow / At Risk)
- Cluster 3 → D/F (Stalled / Needs Review)

**Expected Distribution**:
- A (Excellent): ~12 repos (~0.4%)
- B (Good): ~1415 repos (~42.6%)
- C (At Risk): ~1008 repos (~30.4%)
- D/F (Stalled): ~867 repos (~26.1%)

**Output Artifacts**:
- Model: `ml/repo_health_model.joblib` (contains model + scaler)
- Report: `ml/project_progress_report.csv` (repo grades, sorted by days_since_active)

---

#### 1.2.4 Advanced Analytics
**Component**: `ml/advanced_analytics.py`
**Purpose**: Calculate collaboration & team dynamics metrics

**Data Contract**:
```
Input: COMMITS, REPOSITORIES, AUTHORS (from CSV files)
Processing: Aggregate commits per repo, calculate collaboration score
Output: CSV with strategic insights
```

**Metrics**:
- **collaboration_score**: Number of contributors to reach >50% of commits
  - Formula: Count unique authors where cumulative_share <= 0.50
  - Higher = better distribution
- **bus_factor**: Identified siloed knowledge (1 person = critical)
- **velocity**: Commits per active day per contributor

**Output Artifacts**:
- Report: `ml/advanced_insights.csv` (per-repository metrics)

---

### 1.3 Dashboard Specification

#### Component: `dashboard/app.py`
**Framework**: Streamlit
**URL**: `http://localhost:8501`
**Page Config**: Wide layout, title="Academic Project Mentor", icon="🎓"

**Tabs & Specifications**:

##### Tab 1: Project Progress Grades
**Purpose**: Display repository health grades
**Data Source**: `ml/project_progress_report.csv`
**Metrics Display**:
- Total active projects (count of repos)
- Excellent progress projects (count with grade 'A')
- Stalled projects (count with grade 'D/F')
**Interaction**: Text search by repository name, display matching results

**Success Criteria**:
- File loads without error
- Search returns case-insensitive matches
- Metrics update correctly
- UI displays dataframe with columns: NAME, STARGAZERS_COUNT, status_grade, days_since_active

---

##### Tab 2: Student Fatigue Alerts
**Purpose**: Identify students at burnout risk
**Data Source**: `ml/student_fatigue_report.csv`
**Metrics Display**:
- Count of flagged students
- Display of high-risk developers (sorted by risk score)
**Warning**: Show only students with `needs_mentor_attention == True`

**Success Criteria**:
- File loads without error
- Only flagged developers shown
- Columns shown: AUTHOR_NAME, total_commits, weekend_ratio, late_night_ratio

---

##### Tab 3: Submission Timeline Predictor
**Purpose**: Predict PR merge time for new submissions
**Data Source**: Loaded model `ml/pr_bottleneck_model.joblib`
**Input Form**:
- PR title (text input)
- Creation hour (slider 0-23)
- Submission date (date picker)
**Output**: Predicted days to merge (with confidence interval if applicable)

**Success Criteria**:
- Form inputs validated
- Model inference completes in <1 second
- Output displayed with units
- Error handling for invalid inputs

---

##### Tab 4: Mentor Strategy Insights
**Purpose**: Display collaborative metrics & team dynamics
**Data Source**: `ml/advanced_insights.csv`
**Visualizations**:
- Top 10 repositories by collaboration score
- Repositories with bus factor = 1 (critical risks)
- Student dependence heatmap

**Success Criteria**:
- File loads without error
- Charts render without errors
- Key metrics highlighted with context

---

### 1.4 API/Function Specification

#### Database Connection
**Function**: `get_sqlite_connection()`
**Contract**:
```python
def get_sqlite_connection() -> sqlite3.Connection:
    """
    Returns: Active SQLite connection to repo_metrics.db
    Raises: FileNotFoundError if DB not found at expected path
    Postcondition: Connection has PRAGMA foreign_keys = ON
    """
```

#### Data Sanitization
**Function**: `sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame`
**Contract**:
```python
def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Precondition: df is a pandas DataFrame
    Actions:
      1. Trim whitespace from all string columns
      2. Replace "" / "NA" / "N/A" with None
      3. Convert numeric-like columns to int
      4. Convert date-like columns to ISO 8601 string
      5. Drop rows with all NaN values
    Returns: Cleaned DataFrame (copy, original unmodified)
    Postcondition: DataFrame ready for SQL insertion
    """
```

#### Logging Specification
**Logger Format**: `%(asctime)s - %(levelname)s - %(message)s`
**Levels Required**:
- `INFO`: Major milestones (pipeline start, model training complete, file saved)
- `WARNING`: Minor issues (missing file, empty dataset)
- `ERROR`: Data integrity issues (schema mismatch, insertion failure)
- `CRITICAL`: Pipeline-stopping errors (DB not found, model training failed)

---

## 2. Error Handling Specification

### Error Categories & Responses

| Error Type | Trigger | Response | Log Level |
|-----------|---------|----------|-----------|
| File Not Found | CSV/DB/Schema file missing | Log warning, skip or abort | WARNING |
| Schema Mismatch | CSV columns don't match table schema | Raise ValueError with details | ERROR |
| Empty Dataset | No rows after sanitization | Log warning, attempt next table | WARNING |
| Connection Failure | DB unavailable | Raise with context | CRITICAL |
| Invalid Dates | Unparseable date strings | Coerce to NaT, filter out | WARNING |
| Model Training Failed | Insufficient data or sklearn error | Raise with context | CRITICAL |
| File Encoding | Non-UTF8 files | Use latin-1 fallback | WARNING |

---

## 3. Testing Specification

### Test Scope

#### Unit Tests
**Purpose**: Verify individual functions meet their contracts

**Coverage Areas**:
- `sanitize_dataframe()`: Whitespace trim, NULL conversion, type coercion, row filtering
- `resolve_table_columns()`: Correct extraction of column names
- Feature engineering functions: Correct temporal feature calculation
- Model prediction: Output shape and dtype validation

**Success Criteria**: 100% pass rate, no warnings

#### Integration Tests
**Purpose**: Verify pipeline steps work together

**Test Cases**:
1. CSV → Database migration flow (verify all 7 tables)
2. Database query → Feature engineering → Model training (end-to-end ML pipeline)
3. Dashboard data loading (all 4 CSV files load successfully)

**Success Criteria**: 
- Migration matches row counts exactly
- ML models train without error
- Dashboard renders without exceptions

#### Validation Tests
**Purpose**: Verify outputs match specifications

**Test Cases**:
1. Row counts after migration: USER_TYPES=1, USERS=21, LANGUAGES=70, REPOSITORIES=3320, AUTHORS=15661, COMMITS=146333, PULL_REQUESTS=29875
2. ML model outputs: Correct shape, all values within expected ranges
3. Feature ranges: Ratios between 0-1, commit counts >0, days >= 0

---

## 4. Deployment Specification

### Environment Requirements
- Python 3.8+
- SQLite 3.x
- Dependencies: pandas, scikit-learn, joblib, streamlit, matplotlib

### Initialization Steps
1. Ensure `repo_metrics_schema.sql` and all 7 CSV files present
2. Run `python migrate_to_sqlite.py` → Creates `repo_metrics.db`
3. Run `python ml/train_suite.py` → Trains all 4 ML models, generates reports
4. Run `cd dashboard && streamlit run app.py` → Start dashboard

### Success Criteria for Deployment
- No errors in any step
- Database: 7 tables, correct row counts
- ML: 4 model files (`.joblib`) generated
- Dashboard: Loads at http://localhost:8501 without errors

---

## 5. Specification Compliance Checklist

### Per-Component Verification
- [ ] `migrate_to_sqlite.py`: Follows data sanitization spec, handles all error cases
- [ ] `predict_burnout.py`: Isolation Forest with 5% contamination, outputs flagged list
- [ ] `predict_pr_merge.py`: Random Forest trained on correct features, MAE reported
- [ ] `repo_health_score.py`: K-Means with k=4, correct grade mapping
- [ ] `advanced_analytics.py`: Collaboration score calculated correctly
- [ ] `dashboard/app.py`: All 4 tabs render, interactions work

### Data Contract Verification
- [ ] COMMITS table has 146,333 rows (±5%)
- [ ] PULL_REQUESTS table has 29,875 rows (±5%)
- [ ] All foreign keys intact and valid
- [ ] No NULL values in NOT NULL columns

### ML Output Verification
- [ ] ~89 students flagged for burnout (±10%)
- [ ] PR merge MAE ~11-12 days
- [ ] Project grades distributed A:~12, B:~1415, C:~1008, D/F:~867

---

**Document Version**: 1.0  
**Last Updated**: April 15, 2026  
**Status**: Active - Aligns with current implementation
