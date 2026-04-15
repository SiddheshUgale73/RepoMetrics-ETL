# Test Specification: GitHub Projects Insights

## 1. Unit Test Specifications

### 1.1 Data Sanitization Tests
**Module**: `migrate_to_sqlite.py::sanitize_dataframe()`

#### Test Case: TS-DT-001 - Whitespace Trimming
**Specification Reference**: TECHNICAL_SPEC.md § 1.2.4 - Sanitization Rule 1
**Input**: DataFrame with leading/trailing spaces in string columns
**Expected**: All whitespace trimmed
```python
assert df['column'].str.strip() == df['column']
```

#### Test Case: TS-DT-002 - NULL Value Normalization
**Specification Reference**: TECHNICAL_SPEC.md § 1.2.4 - Sanitization Rule 2
**Input**: DataFrame with "NA", "N/A", "", mixed values
**Expected**: All converted to Python None/NaN
```python
assert df[df.isnull().any(axis=1)].shape[0] > 0  # Has nulls after sanitization
```

#### Test Case: TS-DT-003 - Numeric Column Conversion
**Specification Reference**: TECHNICAL_SPEC.md § 1.2.4 - Sanitization Rule 3
**Input**: DataFrame with columns ending in *_id, *_count, etc.
**Expected**: Converted to int64 dtype
```python
numeric_cols = [c for c in df.columns if any(c.lower().endswith(s) for s in NUMERIC_SUFFIXES)]
for col in numeric_cols:
    assert df[col].dtype in ['int64', 'float64']
```

#### Test Case: TS-DT-004 - Date Column Parsing
**Specification Reference**: TECHNICAL_SPEC.md § 1.2.4 - Sanitization Rule 4
**Input**: DataFrame with date columns in various formats
**Expected**: All parsed to ISO 8601 string format (YYYY-MM-DD HH:MM:SS)
```python
for col in DATE_COLUMNS:
    if col in df.columns:
        assert df[col].str.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$').all()
```

#### Test Case: TS-DT-005 - Empty Row Filtering
**Specification Reference**: TECHNICAL_SPEC.md § 1.2.4 - Sanitization Rule 5
**Input**: DataFrame with all-NULL rows
**Expected**: These rows removed
```python
initial_count = len(df_input)
final_count = len(df_output)
assert final_count <= initial_count
assert not df_output.isnull().all(axis=1).any()  # No all-NULL rows
```

---

### 1.2 Table Column Resolution Tests
**Module**: `migrate_to_sqlite.py::resolve_table_columns()`

#### Test Case: TS-TCR-001 - Correct Column Extraction
**Input**: SQLite connection, table_name='USERS'
**Expected**: Returns ['ID', 'LOGIN', 'NAME', 'TYPE_ID', ...] in order
```python
cols = resolve_table_columns(conn, 'USERS')
assert 'ID' in cols
assert 'TYPE_ID' in cols
assert len(cols) == expected_count
```

#### Test Case: TS-TCR-002 - Error on Missing Table
**Input**: table_name='NONEXISTENT'
**Expected**: Returns empty list or raises error gracefully
```python
try:
    cols = resolve_table_columns(conn, 'NONEXISTENT')
    assert len(cols) == 0
except Exception as e:
    assert 'no such table' in str(e).lower()
```

---

### 1.3 Feature Engineering Tests
**Module**: `ml/predict_burnout.py::feature_engineering()`

#### Test Case: TS-FE-001 - Temporal Feature Calculation
**Input**: DataFrame with COMMIT_DATE column
**Expected**: Correct calculation of day_of_week (0-6), hour_of_day (0-23)
```python
assert df['day_of_week'].min() >= 0
assert df['day_of_week'].max() <= 6
assert df['hour_of_day'].min() >= 0
assert df['hour_of_day'].max() <= 23
```

#### Test Case: TS-FE-002 - Weekend Flag Accuracy
**Input**: Commits on known weekend dates
**Expected**: is_weekend=1 for Sat(5)/Sun(6), 0 otherwise
```python
assert df[df['day_of_week'] == 5]['is_weekend'].all() == 1
assert df[df['day_of_week'] == 0]['is_weekend'].all() == 0
```

#### Test Case: TS-FE-003 - Late-Night Flag Accuracy
**Input**: Commits at various hours
**Expected**: is_late_night=1 for hours 22-4, 0 otherwise
```python
late_night_hours = set(list(range(22, 24)) + list(range(0, 5)))
assert df[df['hour_of_day'].isin(late_night_hours)]['is_late_night'].all() == 1
assert df[df['hour_of_day'] == 12]['is_late_night'].all() == 0
```

#### Test Case: TS-FE-004 - Ratio Calculation Bounds
**Input**: Engineered features DataFrame
**Expected**: weekend_ratio and late_night_ratio in [0.0, 1.0]
```python
assert df['weekend_ratio'].min() >= 0.0
assert df['weekend_ratio'].max() <= 1.0
assert df['late_night_ratio'].min() >= 0.0
assert df['late_night_ratio'].max() <= 1.0
```

#### Test Case: TS-FE-005 - Min Commit Filter
**Input**: Authors with <10 commits
**Expected**: Filtered out from output
```python
assert (df['total_commits'] > 10).all()
assert len(df) < total_authors  # Some filtered
```

---

### 1.4 Model Output Validation Tests
**Module**: `ml/predict_burnout.py::train_burnout_model()`

#### Test Case: TS-MO-001 - Predictions Shape
**Input**: Features DataFrame
**Expected**: Predictions array shape matches input rows
```python
preds = model.predict(X_test)
assert preds.shape[0] == X_test.shape[0]
assert set(preds) == {-1, 1}  # Isolation Forest output
```

#### Test Case: TS-MO-002 - Fatigue Score Assignment
**Input**: Model predictions
**Expected**: fatigue_score = -1 or 1, needs_mentor_attention is boolean
```python
assert df['fatigue_score'].isin([-1, 1]).all()
assert df['needs_mentor_attention'].isin([True, False]).all()
assert (df['needs_mentor_attention'] == (df['fatigue_score'] == -1)).all()
```

#### Test Case: TS-MO-003 - Anomaly Contamination Rate
**Input**: Model fitted on data
**Expected**: ~5% of samples marked as anomalies (±1%)
```python
anomaly_pct = (df['fatigue_score'] == -1).sum() / len(df) * 100
assert 4 <= anomaly_pct <= 6, f"Anomaly % = {anomaly_pct}, expected 5%"
```

---

## 2. Integration Test Specifications

### 2.1 CSV to Database Migration Flow
**Test Suite**: TS-INT-001 - Full Pipeline

#### Test Case: TS-INT-001-A - All Tables Created
**Precondition**: Schema file exists, all 7 CSV files present
**Steps**:
1. Run `migrate_to_sqlite.py`
**Expected Results**:
```python
conn = sqlite3.connect('repo_metrics.db')
tables = ['USER_TYPES', 'USERS', 'LANGUAGES', 'REPOSITORIES', 'AUTHORS', 'COMMITS', 'PULL_REQUESTS']
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    assert cursor.fetchone()[0] > 0
```

#### Test Case: TS-INT-001-B - Exact Row Count Matching
**Expected**: Row counts match specification exactly (±0 tolerance)
```python
expected = {
    'USER_TYPES': 1,
    'USERS': 21,
    'LANGUAGES': 70,
    'REPOSITORIES': 3320,
    'AUTHORS': 15661,
    'COMMITS': 146333,
    'PULL_REQUESTS': 29875
}
for table, expected_count in expected.items():
    actual = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    assert actual == expected_count, f"{table}: expected {expected_count}, got {actual}"
```

#### Test Case: TS-INT-001-C - Foreign Key Integrity
**Expected**: All foreign keys valid (no orphaned records)
```python
# Check USERS.TYPE_ID references USER_TYPES.ID
orphan_check = conn.execute("""
    SELECT COUNT(*) FROM USERS u 
    WHERE u.TYPE_ID NOT IN (SELECT ID FROM USER_TYPES) AND u.TYPE_ID IS NOT NULL
""").fetchone()[0]
assert orphan_check == 0
```

#### Test Case: TS-INT-001-D - No Duplicate Primary Keys
**Expected**: All primary keys unique
```python
for table in tables:
    if table == 'COMMITS':
        pk_check = conn.execute(f"SELECT COUNT(DISTINCT SHA, REPOSITORY_ID) FROM {table}").fetchone()[0]
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    else:
        pk_check = conn.execute(f"SELECT COUNT(DISTINCT ID) FROM {table}").fetchone()[0]
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    assert pk_check == count
```

---

### 2.2 ML Pipeline End-to-End Test
**Test Suite**: TS-INT-002 - Model Training Pipeline

#### Test Case: TS-INT-002-A - Burnout Model Training
**Precondition**: Database populated, SQLite connection available
**Steps**:
1. Extract commits: `extract_commit_data(conn)`
2. Engineer features: `feature_engineering(df)`
3. Train model: `train_burnout_model(features_df)`
**Expected Results**:
```python
# Should succeed without exceptions
assert model is not None
assert results_df.shape[0] > 0
assert 'needs_mentor_attention' in results_df.columns
# Save artifacts
assert os.path.exists('burnout_model.joblib')
assert os.path.exists('student_fatigue_report.csv')
```

#### Test Case: TS-INT-002-B - PR Merge Model Training
**Steps**: Extract PRs → Engineer features → Train Random Forest
**Expected Results**:
```python
assert model is not None
assert mae > 0  # Mean Absolute Error
assert 10 <= mae <= 15  # Expected range
assert os.path.exists('pr_bottleneck_model.joblib')
```

#### Test Case: TS-INT-002-C - Repo Health Clustering
**Steps**: Extract repos → Engineer features → K-Means
**Expected Results**:
```python
assert model is not None
assert scaler is not None
assert results_df['status_grade'].isin(['A', 'B', 'C', 'D/F']).all()
expected_dist = {'A': 12, 'B': 1415, 'C': 1008, 'D/F': 867}
for grade, expected_count in expected_dist.items():
    actual = (results_df['status_grade'] == grade).sum()
    # Allow ±10% variance
    assert abs(actual - expected_count) / expected_count <= 0.1
```

#### Test Case: TS-INT-002-D - Advanced Analytics
**Steps**: Load CSVs → Calculate metrics
**Expected Results**:
```python
assert os.path.exists('advanced_insights.csv')
insights = pd.read_csv('advanced_insights.csv')
assert insights.shape[0] > 0
assert 'collaboration_score' in insights.columns
assert (insights['collaboration_score'] > 0).all()
```

---

### 2.3 Dashboard Data Loading Test
**Test Suite**: TS-INT-003 - Dashboard Assets

#### Test Case: TS-INT-003-A - All CSV Reports Available
**Expected**: All 4 required CSV files exist
```python
ml_dir = 'ml'
required_files = [
    'project_progress_report.csv',
    'student_fatigue_report.csv',
    'advanced_insights.csv'
]
for file in required_files:
    assert os.path.exists(os.path.join(ml_dir, file))
```

#### Test Case: TS-INT-003-B - CSV Data Integrity
**Steps**: Load each CSV, validate schema
**Expected Results**:
```python
# project_progress_report.csv
df = pd.read_csv('ml/project_progress_report.csv')
assert {'NAME', 'STARGAZERS_COUNT', 'status_grade', 'days_since_active'}.issubset(df.columns)

# student_fatigue_report.csv
df = pd.read_csv('ml/student_fatigue_report.csv')
assert 'AUTHOR_NAME' in df.columns
assert 'needs_mentor_attention' in df.columns or len(df) > 0

# advanced_insights.csv
df = pd.read_csv('ml/advanced_insights.csv')
assert 'collaboration_score' in df.columns
```

---

## 3. Validation Test Specifications

### 3.1 Data Contract Validation
**Test Suite**: TS-VAL-001 - Data Correctness

#### Test Case: TS-VAL-001-A - COMMITS Row Count
```python
count = conn.execute("SELECT COUNT(*) FROM COMMITS").fetchone()[0]
tolerance = int(146333 * 0.05)  # ±5%
assert abs(count - 146333) <= tolerance
```

#### Test Case: TS-VAL-001-B - No NULL in NOT NULL Columns
```python
null_check = conn.execute("""
    SELECT COUNT(*) FROM USERS WHERE ID IS NULL OR LOGIN IS NULL
""").fetchone()[0]
assert null_check == 0
```

#### Test Case: TS-VAL-001-C - Valid Date Formats
```python
invalid_dates = conn.execute("""
    SELECT COUNT(*) FROM COMMITS 
    WHERE COMMIT_DATE NOT LIKE '____-__-__ __:__:__'
""").fetchone()[0]
assert invalid_dates == 0
```

---

### 3.2 ML Output Validation
**Test Suite**: TS-VAL-002 - Model Correctness

#### Test Case: TS-VAL-002-A - Burnout Flagged Count
```python
df = pd.read_csv('ml/student_fatigue_report.csv')
flagged_count = len(df)
# Expected ~89 ±10 (within 10% margin)
assert 80 <= flagged_count <= 98
```

#### Test Case: TS-VAL-002-B - Grade Distribution
```python
df = pd.read_csv('ml/project_progress_report.csv')
dist = df['status_grade'].value_counts().to_dict()
# Verify distribution matches spec
assert dist.get('B', 0) > 1000  # Majority should be B
assert dist.get('A', 0) < 50  # Few A grades
```

#### Test Case: TS-VAL-002-C - Ratio Value Ranges
```python
df = pd.read_csv('ml/student_fatigue_report.csv')
assert (df['weekend_ratio'] >= 0).all() and (df['weekend_ratio'] <= 1).all()
assert (df['late_night_ratio'] >= 0).all() and (df['late_night_ratio'] <= 1).all()
```

---

## 4. Regression Test Specifications

**Purpose**: Ensure future changes don't break existing functionality

### 4.1 Baseline Metrics
| Metric | Baseline | Tolerance |
|--------|----------|-----------|
| Migration time | <5 seconds | ±2s |
| ML training time | <30 seconds | ±10s |
| Row count (COMMITS) | 146333 | ±5% |
| Burnout flagged | 89 | ±10% |
| MAE (PR merge) | 11.3 days | ±2 days |

### 4.2 Regression Test: TS-REG-001 - Performance
**Frequency**: After any code changes in migrate_to_sqlite.py or ml/ modules
```python
import time
start = time.time()
migrate()
duration = time.time() - start
assert duration < 7  # 5s baseline + 2s tolerance
```

---

## 5. Test Execution Plan

### Phase 1: Unit Tests (Development Phase)
**When**: During code implementation
**Tools**: pytest, unittest
**Coverage Target**: >80% for critical functions

### Phase 2: Integration Tests (QA Phase)
**When**: After all components complete
**Tools**: pytest with fixtures
**Coverage Target**: End-to-end flows

### Phase 3: Validation Tests (Release Phase)
**When**: Before deployment
**Coverage Target**: All data contracts and ML metrics

### Phase 4: Regression Tests (Maintenance Phase)
**When**: Before each release/update
**Tools**: pytest with baseline snapshots

---

**Document Version**: 1.0  
**Last Updated**: April 15, 2026  
**Status**: Active - Provides testable specifications aligned with TECHNICAL_SPEC.md
