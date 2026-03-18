import streamlit as st
import pandas as pd
import joblib
import os
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(page_title="GitStar Analytics AI", page_icon="🚀", layout="wide")

# Paths to the ML artifacts we generated in Step 2
ML_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml')
repo_rankings_path = os.path.join(ML_DIR, 'repo_health_rankings.csv')
burnout_report_path = os.path.join(ML_DIR, 'burnout_risk_report.csv')
pr_model_path = os.path.join(ML_DIR, 'pr_bottleneck_model.joblib')

st.title("🌟 GitStar Enterprise Analytics")
st.markdown("### Powered by Snowflake & Machine Learning")

# Create 3 Tabs for our 3 ML Models
tab1, tab2, tab3 = st.tabs(["🏗️ Repository Health", "🔥 Developer Burnout Risk", "⏳ PR Merge Predictor"])

# ==========================================
# TAB 1: Repository Health Scoring
# ==========================================
with tab1:
    st.header("Overall Repository Health Grades")
    st.markdown("Repositories are graded from A (Healthy) to F (Abandoned) using K-Means Clustering based on commit frequency, bus factor, and days since last active.")
    
    if os.path.exists(repo_rankings_path):
        repo_df = pd.read_csv(repo_rankings_path)
        
        # High level metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Repos Graded", len(repo_df))
        healthy_count = len(repo_df[repo_df['health_grade'].str.contains('A')])
        col2.metric("A-Grade (Healthy) Repos", healthy_count)
        failing_count = len(repo_df[repo_df['health_grade'].str.contains('D/F')])
        col3.metric("Failing/Abandoned Repos", failing_count)
        
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
    st.header("Developer Flight Risk & Burnout Detection")
    st.markdown("Highlights core contributors exhibiting dangerous work patterns (high weekend/late-night commit ratios) using an Isolation Forest Anomaly Detector.")
    
    if os.path.exists(burnout_report_path):
        burnout_df = pd.read_csv(burnout_report_path)
        
        st.warning(f"🚨 ALERT: {len(burnout_df)} Developers have been flagged as HIGH RISK for burnout.")
        
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
    st.header("Pull Request Merge Time Estimator")
    st.markdown("Predicts how many days a new Pull Request will take to merge based on our Random Forest Regressor.")
    
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
                    
                    st.success(f"**Estimated Time to Merge:** {prediction:.1f} Days ⏱️")
                    
                    if prediction > 14:
                        st.warning("This PR is predicted to become a bottleneck. Assign more reviewers!")
                        
        except Exception as e:
            st.error(f"Failed to load PR Model: {e}")
    else:
        st.error("⚠️ PR Predictor model not found (Not enough training data in Snowflake perhaps?).")
