# Product Requirements Document: GitHub Projects Insights

## 1. Executive Summary

### 1.1 Product Vision
**GitHub Projects Insights** is an AI-powered academic project monitoring suite designed to bridge the visibility gap between student coders and their mentors. By transforming raw Git metadata into actionable behavioral insights, the platform ensures objective project evaluation, identifies team imbalances, and proactively detects student burnout.

### 1.2 Target Audience
*   **Academic Mentors/Guides**: To track multiple project teams efficiently without manual code reviews.
*   **Department Heads**: To ensure consistency in grading and project health across the curriculum.
*   **Students**: Indirectly, by receiving timely support and fair evaluation based on actual contribution data.

---

## 2. Problem Statement
Traditional academic project monitoring relies on periodic "vivas" or subjective progress reports. This leads to several failures:
*   **Late Intervention**: Mentors often discover a team has stalled or a student has dropped out too late in the semester.
*   **Invisible Fatigue**: "Crunch mode" (late-night coding) often remains unseen, leading to student burnout.
*   **The "Bus Factor" Problem**: It is difficult to identify projects dependent on a single student ("Truck/Bus Factor") versus a collaborative effort.

---

## 3. Functional Requirements

### 3.1 Data Ingestion & ETL
*   **Multi-Repo Extraction**: Capable of crawling hundreds of repositories based on specific GitHub search queries (e.g., `repos:>5 followers:>5`).
*   **Resumable Pipeline**: Must support checkpointing (JSON-based) to resume from the last processed user in case of interruptions.
*   **Standardized Schema**: Normalize nested GitHub API responses into a 7-table relational structure (`USERS`, `REPOSITORIES`, `COMMITS`, `AUTHORS`, `PULL_REQUESTS`, `LANGUAGES`, `USER_TYPES`).

### 3.2 AI & Machine Learning Suite
*   **Project Health Scoring (K-Means)**: 
    *   Automatically grade projects from **A (Excellent)** to **F (Stalled)**.
    *   Features: Commit frequency, velocity, and inactivity days.
*   **Burnout Detection (Isolation Forest)**:
    *   Flag students with anomalous work patterns.
    *   Features: Weekend commit ratio, Late-night commit ratio.
*   **PR Merge Predictor (Random Forest)**:
    *   Predict the "Days to Merge" for submitted tasks to identify review bottlenecks.
*   **Advanced Strategic Analytics**:
    *   Calculate **Collaboration Score** and **Student Dependence** (identifying if knowledge is siloed).

### 3.3 Interactive Dashboard (Streamlit)
*   **Project Leaderboard**: View all active projects sorted by health grade.
*   **Risk Watchlist**: Direct alerts for students with high burnout scores or repos with low collaboration.
*   **Predictive Sandbox**: Form-based input to estimate the merge timeline for new submissions.
*   **Strategic Visualization**: Heatmaps showing Inactivity vs. Student Dependence.

---

## 4. Technical Specifications

### 4.1 Technology Stack
| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.8+ |
| **Data Warehouse** | Snowflake (Cloud) |
| **Local Database** | SQLite (Alternative) |
| **ML Framework** | Scikit-Learn |
| **Dashboard** | Streamlit |
| **Visualization** | Matplotlib, Power BI (via SQL/Snowflake) |

### 4.2 Core Algorithms
*   **Isolation Forest**: Used for burnout detection as an unsupervised anomaly detection technique.
*   **K-Means Clustering**: Used for repository health categorization based on activity metrics.
*   **Random Forest Regressor**: Used for predictive modeling of PR lifecycles.

---

## 5. User Stories

| Role | Story | Requirement Met |
| :--- | :--- | :--- |
| **Mentor** | "I want to see which of my 50 project teams are stalling so I can schedule extra meetings." | Tab 1: Project Progress Grade |
| **Guide** | "I want to catch if a student is doing marathon coding sessions at 3 AM." | Tab 2: Fatigue Detection |
| **Evaluator** | "I want to know if one student wrote 90% of the code while others remained inactive." | Tab 4: Student Dependence Metric |

---

## 6. Success Metrics
*   **Intervention Speed**: Time taken to identify a "stalled" project reduced from weeks to <24 hours.
*   **Grading Objectivity**: 100% reliance on data-driven git metrics for contribution evaluation.
*   **Model Accuracy**: PR Merge time prediction within ±1 day error margin.

---

## 7. Roadmap & Future Scope
*   **NLP Analysis**: Sentiment analysis of commit messages and PR comments to gauge team morale.
*   **Predictive Deadline**: Forecasting the final completion date of the project based on current velocity.
*   **Real-time Alerts**: Integration with Email/Slack for instant burnout notifications.
*   **Code Quality Scoring**: Integrating tools like SonarQube or Custom LLM-based code reviews.
