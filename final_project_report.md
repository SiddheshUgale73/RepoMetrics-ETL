# 🎓 Final Year Project Report: AI-Driven Repository Analytics & Insights Engine

**Project Context**: Academic Project Management & Monitoring Suite  
**Objective**: To provide mentors with real-time, AI-driven visibility into student project health and team dynamics.

---

## 1. 🏗️ System Architecture
The platform follows a modern Data Warehouse & Machine Learning pipeline:
1.  **Data Ingestion**: Fetching raw data from GitHub (Commits, PRs, Issues, Languages) via Python scripts.
2.  **Storage (Snowflake/CSV)**: Data is cleaned and stored in a relational format for efficient querying.
3.  **Analytics Layer**: Using SQL to calculate metrics like "Bus Factor" and "Velocity."
4.  **AI/ML Engine**: 
    *   **Isolation Forest** (Anomaly Detection) for Burnout Risk.
    *   **K-Means Clustering** for Repository Health Categorization.
    *   **Random Forest** for predicting PR Merge Times.

## 2. 🧠 Machine Learning Methodology

### 2.1 Anomaly Detection (Burnout Risk)
We utilize **Isolation Forest**, an unsupervised learning algorithm. It isolates student commit patterns that deviate significantly from the "normal" group. 
*   **Feature Set**: (Weekend Commit Ratio, Late Night Commit Ratio).
*   **Academic Goal**: To identify "Flight Risk" or "Crunch Mode" students who may need academic counseling.

### 2.2 Project Health Clustering (Health Grading)
Using **K-Means Clustering**, repositories are grouped based on Euclidean distance across features like `Star Count`, `Days Since Active`, and `Velocity`.
*   **Clusters**: A (Healthy/High Activity), B (Slow/Maintained), C (At Risk), D/F (Abandoned).
*   **Impact**: Mentors can instantly spot "At Risk" teams by their cluster assignment.

## 3. 📊 Experimental Results (Insights)
*   **Scale**: 892 total projects analyzed.
*   **Language Distribution**: JavaScript (39%) and Python (18%) are the dominant tools for development.
*   **Burnout Alert**: AI correctly identified 5+ developers working >90% of their time late at night.
*   **Collaboration Warning**: Identified that **60% of projects** have a Bus Factor of 1, meaning deep knowledge is not being shared within the team.

## 4. 🚀 Impact & Future Scope
*   **Real-world Impact**: This tool prevents project failure by identifying bottlenecks *before* they become critical.
*   **Future Scope**:
    *   **NLP for Code Quality**: Using LLMs to analyze code comments and sentiment.
    *   **Predictive Deadlines**: Predicting the "Final Submission Date" based on current progress.

---
**Prepared For**: College Academic Guides & Mentors  
**Marks Weightage**: 300 Marks Portfolio
