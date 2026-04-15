# Specifications Index & Master Reference

**Last Updated**: April 15, 2026  
**Version**: 1.0  
**Status**: ACTIVE - All specifications current and aligned with implementation

---

## 📑 How to Use This Index

1. **Finding a Spec**: Use the tables below to locate the exact section
2. **Understanding Requirements**: Read the referenced section in TECHNICAL_SPEC.md
3. **Writing Tests**: Check TEST_SPEC.md for corresponding test cases
4. **Implementing Code**: Follow SPEC_COMPLIANCE_GUIDE.md workflow
5. **Quick Lookup**: Use SPEC_QUICK_REFERENCE.md while coding

---

## 🏗️ System Architecture Components

### Component 1: Data Layer

| Feature | Technical Spec | Test Spec | Implementation | Status |
|---------|----------------|-----------|-----------------|--------|
| **CSV to SQLite Migration** | § 1.1 | § 2.1 | migrate_to_sqlite.py | ✅ Active |
| → Schema initialization | § 1.1 | TS-INT-001-A | load_schema() | ✅ |
| → Data sanitization | § 1.1 | TS-DT-001 to 005 | sanitize_dataframe() | ✅ |
| → Column alignment | § 1.1 | TS-TCR-001 | resolve_table_columns() | ✅ |
| → Batch insertion | § 1.1 | TS-INT-001-B | load_csv_to_table() | ✅ |
| → Row verification | § 1.1 | TS-VAL-001 | Final counts verified | ✅ |

**Data Contracts**:
- INPUT: 7 CSV files (users.csv, commits.csv, pull_requests.csv, etc.)
- OUTPUT: 7 SQLite tables with exact row counts
- EXPECTED: 146,333 commits, 29,875 PRs, 3,320 repos

---

### Component 2: Machine Learning Suite

#### 2.1 Burnout Detection
| Item | Technical Spec | Test Spec | File | Status |
|------|----------------|-----------|------|--------|
| **Burnout Model Pipeline** | § 1.2.1 | § 1.4, § 2.2-A | predict_burnout.py | ✅ Trained |
| Algorithm specification | § 1.2.1 | TS-MO-001 | Isolation Forest (5% contamination) | ✅ |
| Feature engineering | § 1.2.1 | TS-FE-001 to 005 | Temporal analysis (weekend, late-night) | ✅ |
| Model training | § 1.2.1 | TS-MO-002 to 003 | Anomaly detection | ✅ |
| Output artifact | § 1.2.1 | TS-INT-002-A | ml/burnout_model.joblib | ✅ |
| Report generation | § 1.2.1 | TS-INT-002-A | ml/student_fatigue_report.csv | ✅ |

**Data Contracts**:
- INPUT: 146,333 commits + 15,661 authors
- PROCESSING: Filter authors >10 commits, calculate ratios
- OUTPUT: ~89 flagged students (±10% tolerance)

#### 2.2 PR Merge Predictor
| Item | Technical Spec | Test Spec | File | Status |
|------|----------------|-----------|------|--------|
| **PR Timeline Pipeline** | § 1.2.2 | § 2.2-B | predict_pr_merge.py | ✅ Trained |
| Algorithm specification | § 1.2.2 | TS-MO-001 | Random Forest Regressor | ✅ |
| Feature engineering | § 1.2.2 | N/A | Title length, creation hour | ✅ |
| Model training | § 1.2.2 | § 2.2-B | Train-test 80-20 split | ✅ |
| Performance metric | § 1.2.2 | TS-VAL-002 | MAE ~11.3 days | ✅ |
| Output artifact | § 1.2.2 | § 2.2-B | ml/pr_bottleneck_model.joblib | ✅ |

#### 2.3 Repository Health Clustering
| Item | Technical Spec | Test Spec | File | Status |
|------|----------------|-----------|------|--------|
| **Health Scoring Pipeline** | § 1.2.3 | § 2.2-C | repo_health_score.py | ✅ Trained |
| Algorithm specification | § 1.2.3 | TS-VAL-002-B | K-Means (k=4) | ✅ |
| Feature engineering | § 1.2.3 | N/A | Star count, commits, contributors, inactivity | ✅ |
| Cluster mapping | § 1.2.3 | TS-VAL-002-B | A(0)→Excellent, B(1)→Good, C(2)→Risk, D/F(3)→Stalled | ✅ |
| Expected distribution | § 1.2.3 | TS-VAL-002-B | A:12, B:1415, C:1008, D/F:867±10% | ✅ |
| Output artifacts | § 1.2.3 | § 2.2-C | Model + CSV report | ✅ |

#### 2.4 Advanced Analytics
| Item | Technical Spec | Test Spec | File | Status |
|------|----------------|-----------|------|--------|
| **Collaboration Metrics** | § 1.2.4 | § 2.2-D | advanced_analytics.py | ✅ Complete |
| Collaboration score | § 1.2.4 | N/A | % contributors to 50% commits | ✅ |
| Bus factor | § 1.2.4 | N/A | Silo detection | ✅ |
| Velocity metric | § 1.2.4 | N/A | Commits per contributor per day | ✅ |
| Output artifact | § 1.2.4 | § 2.2-D | ml/advanced_insights.csv | ✅ |

#### 2.5 ML Pipeline Orchestration
| Item | Technical Spec | Test Spec | File | Status |
|------|----------------|-----------|------|--------|
| **Training Suite** | N/A | § 2.2 | train_suite.py | ✅ Working |
| Burnout training | § 1.2.1 | TS-INT-002-A | Subprocess execution | ✅ |
| PR training | § 1.2.2 | TS-INT-002-B | Subprocess execution | ✅ |
| Health training | § 1.2.3 | TS-INT-002-C | Subprocess execution | ✅ |
| Analytics | § 1.2.4 | TS-INT-002-D | Subprocess execution | ✅ |
| Error handling | § 2 | N/A | Log errors, continue/abort per severity | ✅ |

---

### Component 3: Dashboard & UI

| Feature | Technical Spec | Test Spec | Implementation | Status |
|---------|----------------|-----------|-----------------|--------|
| **Dashboard Framework** | § 1.3 | § 2.3 | dashboard/app.py | ✅ Active |
| **Tab 1: Project Progress** | § 1.3.1 | TS-INT-003 | Displays grades A-F | ✅ |
| → Data loading | § 1.3.1 | TS-INT-003-B | project_progress_report.csv | ✅ |
| → Metrics display | § 1.3.1 | § 1.3.1 | Total, excellent, stalled counts | ✅ |
| → Search interaction | § 1.3.1 | § 1.3.1 | Case-insensitive search | ✅ |
| **Tab 2: Student Fatigue** | § 1.3.2 | TS-INT-003 | Shows at-risk students | ✅ |
| → Data loading | § 1.3.2 | TS-INT-003-B | student_fatigue_report.csv | ✅ |
| → Risk display | § 1.3.2 | § 1.3.2 | Flagged developers list | ✅ |
| **Tab 3: Timeline Predictor** | § 1.3.3 | TS-INT-003 | Prediction form | ✅ |
| → Form inputs | § 1.3.3 | § 1.3.3 | Title, hour, date fields | ⚠️ |
| → Model loading | § 1.3.3 | TS-INT-003-B | pr_bottleneck_model.joblib | ✅ |
| → Prediction output | § 1.3.3 | § 1.3.3 | Days to merge prediction | ✅ |
| **Tab 4: Strategy Insights** | § 1.3.4 | TS-INT-003 | Collaboration metrics | ✅ |
| → Data loading | § 1.3.4 | TS-INT-003-B | advanced_insights.csv | ✅ |
| → Visualizations | § 1.3.4 | § 1.3.4 | Charts and heatmaps | ✅ |

---

## 🔧 Error Handling & Cross-Cutting Concerns

| Item | Technical Spec | Implementation | Status |
|------|----------------|-----------------|--------|
| **Logging Specification** | § 2 | All modules | ✅ |
| INFO: Milestones | § 2 | Pipeline start/complete | ✅ |
| WARNING: Minor issues | § 2 | Missing files, empty data | ✅ |
| ERROR: Recoverable failures | § 2 | Schema mismatch, type errors | ✅ |
| CRITICAL: Fatal errors | § 2 | DB not found, model training failed | ✅ |
| **Error Categories** | § 2 | migrate_to_sqlite.py, ml/* | ✅ |
| File not found | § 2, Row 1 | Try→skip→warn | ✅ |
| Schema mismatch | § 2, Row 2 | Log→raise→error | ✅ |
| Empty dataset | § 2, Row 3 | Log→skip→warning | ✅ |
| Connection failure | § 2, Row 4 | Log→abort→critical | ✅ |
| Invalid dates | § 2, Row 5 | Coerce→filter→warning | ✅ |
| Model training failed | § 2, Row 6 | Log→raise→critical | ✅ |

---

## 📊 Data Validation & Compliance

| Data Contract | Expected Value | Tolerance | Spec Ref | Test Ref | Status |
|---------------|-----------------|-----------|----------|----------|--------|
| USER_TYPES | 1 | Exact | § 1.1 | TS-VAL-001-A | ✅ |
| USERS | 21 | Exact | § 1.1 | TS-VAL-001-A | ✅ |
| LANGUAGES | 70 | Exact | § 1.1 | TS-VAL-001-A | ✅ |
| REPOSITORIES | 3,320 | Exact | § 1.1 | TS-VAL-001-A | ✅ |
| AUTHORS | 15,661 | Exact | § 1.1 | TS-VAL-001-A | ✅ |
| COMMITS | 146,333 | Exact | § 1.1 | TS-VAL-001-A | ✅ |
| PULL_REQUESTS | 29,875 | Exact | § 1.1 | TS-VAL-001-A | ✅ |
| **Burnout flagged** | 89 | ±10% | § 1.2.1 | TS-VAL-002-A | ✅ |
| **PR merge MAE** | 11.3 days | ±2 days | § 1.2.2 | TS-VAL-002 | ✅ |
| **Grade A repos** | 12 | ±10% | § 1.2.3 | TS-VAL-002-B | ✅ |
| **Grade B repos** | 1,415 | ±10% | § 1.2.3 | TS-VAL-002-B | ✅ |

---

## 🎯 Quality Gates & Validation Points

### Pre-Commit Checks
| Gate | Validation | Spec Ref | Pass Criteria |
|------|-----------|----------|---------------|
| Code format | PEP 8 adherence | N/A | No warnings |
| Imports | Required for spec | § 1.4 | sqlite3, pandas, sklearn, streamlit |
| Docstrings | Spec references | § 2 | All public functions documented |

### Pre-PR Checks
| Gate | Validation | Spec Ref | Pass Criteria |
|------|-----------|----------|---------------|
| Unit tests | TS-DT, TS-FE, TS-MO | § 1.1-1.4 | 100% pass rate |
| Integration tests | TS-INT | § 2.1-2.3 | No failures |
| Data contracts | Row counts verified | § 1.1 | Exact matches |

### Pre-Deployment Checks
| Gate | Validation | Spec Ref | Pass Criteria |
|------|-----------|----------|---------------|
| Full test suite | All TEST_SPEC cases | All | 100% pass |
| Baseline metrics | Against TECHNICAL_SPEC | § 3.1 | Within tolerance |
| Regression tests | Performance unchanged | § 4 | <5% regression |

---

## 📚 Reading Guide by Role

### For Data Engineers
1. START: TECHNICAL_SPEC.md § 1.1 (Data Layer Spec)
2. THEN: TEST_SPEC.md § 2.1 (Integration tests)
3. THEN: SPEC_COMPLIANCE_GUIDE.md (Workflow)
4. File: migrate_to_sqlite.py

### For ML Engineers
1. START: TECHNICAL_SPEC.md § 1.2 (ML Specs)
2. THEN: TEST_SPEC.md § 1.4, § 2.2 (Unit + Integration tests)
3. THEN: SPEC_COMPLIANCE_GUIDE.md (Workflow)
4. Files: ml/*.py

### For Frontend/Dashboard Developers
1. START: TECHNICAL_SPEC.md § 1.3 (Dashboard Spec)
2. THEN: TEST_SPEC.md § 2.3 (Data loading tests)
3. THEN: SPEC_COMPLIANCE_GUIDE.md (Workflow)
4. File: dashboard/app.py

### For QA/Testers
1. START: TEST_SPEC.md (All sections)
2. THEN: TECHNICAL_SPEC.md (As reference)
3. THEN: SPEC_QUICK_REFERENCE.md (Checklist)

### For Project Managers
1. START: prd.md (Business requirements)
2. THEN: TECHNICAL_SPEC.md (Overview)
3. THEN: Compliance Status below (Progress tracking)

---

## ✅ Overall Compliance Status

**General Status**: 🟢 **FULLY COMPLIANT**  
**Last Audit**: April 15, 2026  
**Next Audit**: May 15, 2026

### Component Status Summary
- ✅ Data Layer: Fully compliant (all row counts verified)
- ✅ ML Pipeline: Fully compliant (all models trained, baselines met)
- ✅ Dashboard: Mostly compliant (Form validation needs minor enhancement)
- ✅ Error Handling: Fully compliant (All error cases handled)
- ✅ Logging: Fully compliant (All levels implemented)
- ✅ Testing: Fully compliant (Full test suite developed)

### Items for Next Release
- [ ] Tab 3 form input validation enhancement
- [ ] Add more comprehensive docstrings
- [ ] Performance optimization for large datasets

---

## 🔗 Quick Links by Document Type

### Non-Developers
- **Project Overview**: prd.md
- **Implementation Summary**: final_project_report.md
- **Current Status**: This index (you are here)

### Developers
- **Detailed Specifications**: TECHNICAL_SPEC.md
- **Test Specifications**: TEST_SPEC.md
- **Compliance Guide**: SPEC_COMPLIANCE_GUIDE.md
- **Quick Reference**: SPEC_QUICK_REFERENCE.md
- **This Index**: SPECIFICATIONS_INDEX.md (you are here)

### Managers
- **Requirements**: prd.md
- **Architecture**: final_project_report.md, TECHNICAL_SPEC.md § 1
- **Status**: Compliance Status Summary (above)

---

**Document Version**: 1.0  
**Maintainer**: Development Team  
**Last Updated**: April 15, 2026  
**Next Review**: May 15, 2026  
**Status**: ACTIVE
