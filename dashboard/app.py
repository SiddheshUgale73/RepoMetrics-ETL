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
advanced_insights_path = os.path.join(ML_DIR, 'advanced_insights.csv')

st.title("🌟 GitStar Enterprise Analytics")
st.markdown("### Powered by Snowflake & Machine Learning")

# Create 4 Tabs for our ML Models
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Repository Health", "🔥 Developer Burnout Risk", "⏳ PR Merge Predictor", "📊 Strategic Insights"])

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

# ==========================================
# TAB 4: Strategic Repository Insights
# ==========================================
with tab4:
    st.header("📊 Strategic Repository Insights")
    st.markdown("Advanced metrics for engineering leaders to identify technical debt, team silos, and project momentum.")
    
    if os.path.exists(advanced_insights_path):
        adv_df = pd.read_csv(advanced_insights_path)
        
        # High level summary metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Bus Factor", round(adv_df['BUS_FACTOR'].mean(), 1))
        m2.metric("Stale Repos (>30d)", len(adv_df[adv_df['STALENESS'] > 30]))
        m3.metric("Avg Project Velocity", f"{adv_df['VELOCITY'].mean():.1f} commits/wk")
        
        st.divider()
        
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Repository Risk Matrix")
            st.dataframe(adv_df[['NAME', 'BUS_FACTOR', 'VELOCITY', 'STALENESS', 'TOP_CONTRIBUTOR_CONCENTRATION']], use_container_width=True)
            
        with col_right:
            st.subheader("⚠️ High Risk Watchlist")
            # Filter for "At Risk" repos: Bus Factor < 2 or Staleness > 60
            at_risk = adv_df[(adv_df['BUS_FACTOR'] <= 1) | (adv_df['STALENESS'] > 60)]
            if not at_risk.empty:
                for _, row in at_risk.iterrows():
                    reason = []
                    if row['BUS_FACTOR'] <= 1: reason.append("Low Bus Factor (Silo)")
                    if row['STALENESS'] > 60: reason.append("Stale (>60 days)")
                    st.error(f"**{row['NAME']}**\n- {', '.join(reason)}")
            else:
                st.success("No critical risks detected in current repositories.")
                
        # Risk Heatmap
        st.subheader("Maintenance Risk: Staleness vs Concentration")
        fig, ax = plt.subplots(figsize=(10, 5))
        scatter = ax.scatter(adv_df['STALENESS'], adv_df['TOP_CONTRIBUTOR_CONCENTRATION'], 
                           s=adv_df['BUS_FACTOR']*100, alpha=0.5, c=adv_df['VELOCITY'], cmap='viridis')
        ax.set_xlabel("Days Since Last Commit (Staleness)")
        ax.set_ylabel("Top Contributor Concentration (%)")
        plt.colorbar(scatter, label='Commit Velocity')
        st.pyplot(fig)
        st.caption("Circle size represents Bus Factor. Color represents velocity (commits/week).")
        
    else:
        st.error("⚠️ Advanced Insights data not found. Please run the ML pipeline first.")

