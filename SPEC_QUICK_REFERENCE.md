# Specification Quick Reference Card

**Print This | Tape to Monitor**

---

## 🎯 Spec-Driven Development Workflow

```
1. READ SPEC                2. WRITE TESTS            3. IMPLEMENT CODE
   ↓                           ↓                           ↓
TECHNICAL_SPEC.md    →    TEST_SPEC.md       →        Source Code
Find your component       Find test cases           Code to pass tests
Read requirements        Understand validation      Reference spec
```

---

## 📋 Key Specs at a Glance

### Data Layer (migrate_to_sqlite.py)
| What | Spec Ref | Key Metric |
|------|----------|-----------|
| Input | 7 CSV files | All present, no corruption |
| Sanitization | § 1.1 | Trim spaces, convert NULLs, parse types |
| Output | SQLite | 146,333 commits (exact) |
| Tests | TS-DT-001 to 005, § 2.1 | All migration tests pass |

### ML Models
| Model | Citation | Target Output | Baseline |
|-------|----------|----------------|----------|
| Burnout (Isolation Forest) | § 1.2.1 | CSV with flagged students | ~89 students ±10% |
| PR Predictor (Random Forest) | § 1.2.2 | Model + MAE metric | MAE ~11 days |
| Health Clustering (K-Means) | § 1.2.3 | Grades A-F per repo | A:12, B:1415, C:1008, D/F:867 |
| Advanced Analytics | § 1.2.4 | Collaboration scores | >0 per repository |

### Dashboard (dashboard/app.py)
| Tab | Data Source | Spec Ref | Key Interaction |
|-----|-------------|----------|-----------------|
| 1. Project Progress | project_progress_report.csv | § 1.3.1 | Search by repo name |
| 2. Student Fatigue | student_fatigue_report.csv | § 1.3.2 | Show flagged students |
| 3. Timeline Predictor | pr_bottleneck_model.joblib | § 1.3.3 | Predict PR merge time |
| 4. Strategy Insights | advanced_insights.csv | § 1.3.4 | Display collaboration metrics |

---

## ✅ Compliance Checklist (Before Code Review)

- [ ] Code matches TECHNICAL_SPEC.md section
- [ ] All test cases pass (TEST_SPEC.md section)
- [ ] Error handling follows specification
- [ ] Logging: INFO (milestone), WARNING (skip), ERROR (fail), CRITICAL (abort)
- [ ] Output values in expected ranges
- [ ] No baseline metric regressions

---

## 🔗 File Location Reference

```
Project Root/
├── TECHNICAL_SPEC.md          ← Read this first
├── TEST_SPEC.md               ← Tests for each spec
├── SPEC_COMPLIANCE_GUIDE.md   ← How to use specs
├── prd.md                     ← Business requirements
├── final_project_report.md    ← Implementation summary
│
├── migrate_to_sqlite.py       → Spec: § 1.1, Tests: § 2.1
├── ml/
│   ├── predict_burnout.py     → Spec: § 1.2.1, Tests: § 1.4, § 2.2-A
│   ├── predict_pr_merge.py    → Spec: § 1.2.2, Tests: § 2.2-B
│   ├── repo_health_score.py   → Spec: § 1.2.3, Tests: § 2.2-C
│   ├── advanced_analytics.py  → Spec: § 1.2.4, Tests: § 2.2-D
│   └── train_suite.py         → Orchestrates all models
├── dashboard/
│   └── app.py                 → Spec: § 1.3, Tests: § 2.3
```

---

## 🧪 Quick Test Commands

```bash
# Run all tests
pytest -v

# Test specific component (example: migration)
pytest -k "TS-INT-001"

# Test specific model (example: burnout)
pytest -k "burnout"

# Validate data contracts
python verify_data_contracts.py

# Check row counts
sqlite3 repo_metrics.db "SELECT COUNT(*) FROM COMMITS;"
# Expected: 146333
```

---

## 📊 Row Count Verification (Data Contract)

Run after migration:
```sql
SELECT COUNT(*) as USER_TYPES FROM USER_TYPES;         -- Expected: 1
SELECT COUNT(*) as USERS FROM USERS;                   -- Expected: 21
SELECT COUNT(*) as LANGUAGES FROM LANGUAGES;           -- Expected: 70
SELECT COUNT(*) as REPOSITORIES FROM REPOSITORIES;     -- Expected: 3320
SELECT COUNT(*) as AUTHORS FROM AUTHORS;               -- Expected: 15661
SELECT COUNT(*) as COMMITS FROM COMMITS;               -- Expected: 146333
SELECT COUNT(*) as PULL_REQUESTS FROM PULL_REQUESTS;   -- Expected: 29875
```

---

## 🎓 Common Developer Questions

### Q: "Where do I find the spec for function X?"
**A**: Search for function name in TECHNICAL_SPEC.md § 1.4

### Q: "How do I know my code is correct?"
**A**: Run tests in TEST_SPEC.md corresponding section. If all pass → compliant

### Q: "Can I change the spec?"
**A**: Only if spec is wrong/impossible. Document rationale. Update TEST_SPEC.md too.

### Q: "What if output doesn't match specification?"
**A**: 
1. Check test case (TEST_SPEC.md)
2. Debug code to match spec
3. If spec needs change: Document why, update both spec files

### Q: "How often should I check compliance?"
**A**: 
- Before commit: Check your section only
- Before PR: Run all tests for changed components
- Before merge: Full test suite + baseline metrics

---

## 🚨 Error Handling Reference

| Error Type | Spec Ref | Response | Log Level |
|-----------|----------|----------|-----------|
| File not found | § 2 | Log & skip or abort | WARNING/ERROR |
| Schema mismatch | § 2 | Raise ValueError | ERROR |
| NULL in NOT NULL | § 2 | Raise constraint error | CRITICAL |
| Model training failed | § 2 | Raise with context | CRITICAL |
| Empty dataset | § 2 | Log warning, continue | WARNING |
| Date parse error | § 2 | Coerce to NaT, filter | WARNING |

---

## 📈 Baseline Metrics (Regression Testing)

| Metric | Baseline | ±Tolerance | Spec Ref |
|--------|----------|-----------|----------|
| COMMITS count | 146,333 | ±7,316 (5%) | § 3.1 |
| Burnout flagged | 89 | ±9 (10%) | § 1.2.1 |
| PR merge MAE | 11.3 days | ±2 days | § 1.2.2 |
| Grade A repos | 12 | ±5 | § 1.2.3 |
| Migration time | <5 sec | ±2 sec | § 4 |

---

## 🔄 Weekly Compliance Review

**Every Monday 9 AM**:
- [ ] Run full test suite
- [ ] Check all row counts vs spec
- [ ] Run regression tests
- [ ] Review any spec violation logs
- [ ] Update SPEC_COMPLIANCE_GUIDE.md status

---

## 📚 Document Hierarchy

```
Product Requirements (prd.md)
    ↓
Technical Specification (TECHNICAL_SPEC.md)
    ├→ Test Specification (TEST_SPEC.md)
    ├→ Compliance Guide (SPEC_COMPLIANCE_GUIDE.md)
    └→ Implementation (Code)
    
Test Results ← Validates alignment
```

---

**For Questions**: Refer to appropriate spec section  
**For Issues**: Check TEST_SPEC.md for test cases  
**For Changes**: Update TECHNICAL_SPEC.md + TEST_SPEC.md + this file
