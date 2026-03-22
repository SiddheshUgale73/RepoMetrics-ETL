import streamlit as st
import pandas as pd
import joblib
import os
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(page_title="Academic Project Mentor", page_icon="🎓", layout="wide")

# Paths to the ML artifacts we generated in Step 2
ML_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml')
repo_rankings_path = os.path.join(ML_DIR, 'project_progress_report.csv')
burnout_report_path = os.path.join(ML_DIR, 'student_fatigue_report.csv')
pr_model_path = os.path.join(ML_DIR, 'pr_bottleneck_model.joblib')
advanced_insights_path = os.path.join(ML_DIR, 'advanced_insights.csv')

st.title("🎓 Github Students Insights")
st.markdown("### Mentorship Support System via Snowflake & AI")

# Create 4 Tabs for our ML Models
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Project Progress", "🔥 Student Fatigue Alert", "⏳ Submission Timeline Predictor", "📊 Mentor Strategy Insights"])

# ==========================================
# TAB 1: Repository Health Scoring
# ==========================================
with tab1:
    st.header("Daily Project Progress Grades")
    st.markdown("Projects are graded from A (Excellent) to F (Stalled) using machine learning based on commit frequency and team consistency.")
    
    if os.path.exists(repo_rankings_path):
        repo_df = pd.read_csv(repo_rankings_path)
        
        # High level metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Student Projects", len(repo_df))
        healthy_count = len(repo_df[repo_df['status_grade'].str.contains('A')])
        col2.metric("Excellent Progress Projects", healthy_count)
        failing_count = len(repo_df[repo_df['status_grade'].str.contains('D/F')])
        col3.metric("Stalled Projects", failing_count)
        
        st.divider()
        
        # Interactive Search
        st.subheader("🔍 Search Your Repository")
        search_query = st.text_input("Enter Repository Name to see its grade:", "")
        if search_query:
            result = repo_df[repo_df['NAME'].str.contains(search_query, case=False, na=False)]
            st.dataframe(result, use_container_width=True)
            
        st.subheader("Leaderboard (Top 50 Most Active)")
        st.dataframe(repo_df.head(50), use_container_width=True)
    else:
        st.error("⚠️ Repo Health model data not found. Please run the ML pipeline first.")

# ==========================================
# TAB 2: Developer Burnout Risk
# ==========================================
with tab2:
    st.header("Student Fatigue & Overwork Detection")
    st.markdown("Highlights students with irregular work patterns (late-night or marathon coding sessions) who may need mentor support.")
    
    if os.path.exists(burnout_report_path):
        burnout_df = pd.read_csv(burnout_report_path)
        
        st.error(f"🚨 ALERT: {len(burnout_df)} Students identified as requiring MENTOR ATTENTION.")
        
        st.dataframe(burnout_df[['AUTHOR_NAME', 'total_commits', 'weekend_ratio', 'late_night_ratio', 'commits_per_day']], use_container_width=True)
        
        # Visualize
        st.subheader("Risk Distribution Pattern")
        fig, ax = plt.subplots(figsize=(8,4))
        ax.scatter(burnout_df['weekend_ratio'], burnout_df['late_night_ratio'], color='red', alpha=0.6)
        ax.set_xlabel("Weekend Commit Ratio")
        ax.set_ylabel("Late Night Commit Ratio")
        st.pyplot(fig)
    else:
        st.error("⚠️ Burnout model data not found. Please run the ML pipeline first.")

# ==========================================
# TAB 3: PR Bottleneck Predictor
# ==========================================
with tab3:
    st.header("Task Submission Timeline Predictor")
    st.markdown("Predicts how long it will take for a student's PR (Pull Request) to be reviewed and merged by the Guide.")
    
    if os.path.exists(pr_model_path):
        try:
            pr_model = joblib.load(pr_model_path)
            
            # Interactive prediction form
            with st.form("pr_form"):
                st.subheader("Estimate Merge Time for a New PR")
                col1, col2 = st.columns(2)
                
                with col1:
                    title_length = st.slider("PR Title Length (characters):", 10, 150, 50)
                    hour = st.slider("Hour of Day Opened (0-23):", 0, 23, 14)
                    
                with col2:
                    dayOfWeek = st.selectbox("Day of Week Opened:", [0,1,2,3,4,5,6], format_func=lambda x: ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][x])
                    exp = st.number_input("Author's Previous PR Count to this repo:", min_value=0, max_value=1000, value=5)
                
                submit = st.form_submit_button("🔮 Predict Days to Merge")
                
                if submit:
                    # Create matching DataFrame for the model: ['title_length', 'created_hour', 'created_day_of_week', 'author_experience']
                    input_data = pd.DataFrame({
                        'title_length': [title_length],
                        'created_hour': [hour],
                        'created_day_of_week': [dayOfWeek],
                        'author_experience': [exp]
                    })
                    
                    prediction = pr_model.predict(input_data)[0]
                    
                    st.success(f"**Predicted Review Time:** {prediction:.1f} Days ⏱️")
                    
                    if prediction > 14:
                        st.warning("This PR is predicted to become a bottleneck. Assign more reviewers!")
                        
        except Exception as e:
            st.error(f"Failed to load PR Model: {e}")
    else:
        st.error("⚠️ PR Predictor model not found (Not enough training data in Snowflake perhaps?).")

# ==========================================
# TAB 4: Strategic Repository Insights
# ==========================================
with tab4:
    st.header("📊 Mentor's Strategic Project Insights")
    st.markdown("Broad metrics for mentors to identify team imbalances and overall research momentum.")
    
    if os.path.exists(advanced_insights_path):
        adv_df = pd.read_csv(advanced_insights_path)
        
        # High level summary metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Collaboration Score", round(adv_df['COLLABORATION_SCORE'].mean(), 1))
        m2.metric("Stalled Projects (>30d)", len(adv_df[adv_df['INACTIVITY_DAYS'] > 30]))
        m3.metric("Avg Student Velocity", f"{adv_df['VELOCITY'].mean():.1f} updates/wk")
        
        st.divider()
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Project Activity Matrix")
            st.dataframe(adv_df[['NAME', 'COLLABORATION_SCORE', 'VELOCITY', 'INACTIVITY_DAYS', 'DEPENDENCE_ON_TOP_STUDENT']], use_container_width=True)
            
        with col_right:
            st.subheader("⚠️ High Risk Watchlist")
            # Filter for "At Risk" projects: Collaboration < 2 or Inactivity > 60
            at_risk = adv_df[(adv_df['COLLABORATION_SCORE'] <= 1) | (adv_df['INACTIVITY_DAYS'] > 60)]
            if not at_risk.empty:
                for _, row in at_risk.iterrows():
                    reason = []
                    if row['COLLABORATION_SCORE'] <= 1: reason.append("Low Collaboration (Siloed)")
                    if row['INACTIVITY_DAYS'] > 60: reason.append("Inactive (>60 days)")
                    st.error(f"**{row['NAME']}**\n- {', '.join(reason)}")
            else:
                st.success("No critical risks detected in current repositories.")
                
        # Risk Heatmap
        st.subheader("Participation Risk: Inactivity vs Student Dependence")
        fig, ax = plt.subplots(figsize=(10, 5))
        scatter = ax.scatter(adv_df['INACTIVITY_DAYS'], adv_df['DEPENDENCE_ON_TOP_STUDENT'], 
                           s=adv_df['COLLABORATION_SCORE']*100, alpha=0.5, c=adv_df['VELOCITY'], cmap='viridis')
        ax.set_xlabel("Days Since Last Update (Inactivity)")
        ax.set_ylabel("Dependence on Leader (%)")
        plt.colorbar(scatter, label='Update Velocity')
        st.pyplot(fig)
        st.caption("Circle size represents Collaboration Level. Color represents update frequency.")
        
    else:
        st.error("⚠️ Advanced Insights data not found. Please run the ML pipeline first.")

