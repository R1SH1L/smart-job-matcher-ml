import streamlit as st
import pandas as pd
from scraper import scrape_and_save_jobs, extract_all_skills
from matcher import match_jobs
from data_handler import load_jobs_from_csv, get_csv_stats
from clustering_model import JobClusteringModel
from daily_monitor import DailyJobMonitor
import plotly.express as px

st.set_page_config(
    page_title="Smart Job Matcher",
    page_icon="🎯",
    layout="centered"
)

if 'jobs_df' not in st.session_state:
    st.session_state.jobs_df = pd.DataFrame()
if 'available_skills' not in st.session_state:
    st.session_state.available_skills = []

st.title("🎯 Smart Job Matcher")
st.markdown("*Scrape jobs → Save to CSV → Match with your skills*")

st.sidebar.header("📊 Data Management")

csv_stats = get_csv_stats()
if csv_stats["exists"]:
    st.sidebar.success("✅ CSV Database Found")
    st.sidebar.metric("Total Jobs", csv_stats["total_jobs"])
    st.sidebar.metric("Companies", csv_stats["companies"])
    st.sidebar.write(f"**Last Updated:** {csv_stats['last_updated']}")
    
    if csv_stats.get("top_skills"):
        st.sidebar.write("**Top Skills:**")
        for skill in csv_stats["top_skills"][:5]:
            st.sidebar.write(f"• {skill}")
else:
    st.sidebar.warning("⚠️ No CSV database found")
    st.sidebar.info("💡 Start by scraping some jobs!")

if st.sidebar.button("📂 Load Existing Jobs"):
    with st.spinner("Loading jobs from CSV..."):
        st.session_state.jobs_df = load_jobs_from_csv()
        if not st.session_state.jobs_df.empty:
            st.session_state.available_skills = extract_all_skills(st.session_state.jobs_df)
            st.sidebar.success(f"Loaded {len(st.session_state.jobs_df)} jobs!")
        else:
            st.sidebar.error("No jobs found in CSV")

st.header("🔍 Job Scraping")

col1, col2 = st.columns([2, 1])
with col1:
    keyword = st.text_input("Search Keyword", value="software developer")
with col2:
    pages = st.number_input("Pages", min_value=1, max_value=5, value=2)

if st.button("🚀 Scrape New Jobs", type="primary"):
    if not keyword.strip():
        st.error("⚠️ Please enter a search keyword")
    else:
        with st.spinner(f"Scraping '{keyword}' jobs..."):
            try:
                new_jobs = scrape_and_save_jobs(keyword, pages, update_csv=True)
                
                if not new_jobs.empty:
                    st.session_state.jobs_df = load_jobs_from_csv()
                    st.session_state.available_skills = extract_all_skills(st.session_state.jobs_df)
                    
                    st.success(f"✅ Scraped {len(new_jobs)} new jobs!")
                    st.dataframe(new_jobs.head())
                else:
                    st.error("❌ No real jobs were scraped. This could be due to:")
                    st.markdown("""
                    - Website structure changes
                    - Network connectivity issues
                    - Website blocking requests
                    - No jobs available for this keyword
                    
                    Try a different keyword or check your internet connection.
                    """)
                    
            except Exception as e:
                st.error(f"Error during scraping: {e}")

if st.session_state.available_skills:
    st.header("🛠️ Select Your Skills")
    st.info(f"📊 {len(st.session_state.available_skills)} skills available from {len(st.session_state.jobs_df)} jobs")
    
    cols = st.columns(3)
    selected_skills = []
    
    for i, skill in enumerate(st.session_state.available_skills):
        with cols[i % 3]:
            if st.checkbox(skill, key=f"skill_{i}"):
                selected_skills.append(skill)
    
    if selected_skills:
        st.info(f"**Selected:** {', '.join(selected_skills)}")
        user_skills = ", ".join(selected_skills)
    else:
        user_skills = ""
    
    with st.expander("➕ Add Custom Skills"):
        custom = st.text_input("Additional skills (comma-separated)")
        if custom:
            user_skills = f"{user_skills}, {custom}" if user_skills else custom

elif not st.session_state.jobs_df.empty:
    st.header("🛠️ Enter Your Skills")
    st.warning("⚠️ No skills could be extracted from job data")
    user_skills = st.text_input("Skills (comma-separated)", 
                               placeholder="Python, SQL, Machine Learning")
else:
    st.header("🛠️ Get Started")
    st.info("👆 Please scrape some jobs first to get started!")
    user_skills = ""

if user_skills and not st.session_state.jobs_df.empty:
    if st.button("🎯 Find Matching Jobs", type="primary"):
        with st.spinner("Finding matches..."):
            try:
                matches = match_jobs(user_skills, st.session_state.jobs_df)
                
                if matches.empty:
                    st.warning("🔍 No matches found. Try different or broader skills.")
                else:
                    st.success(f"✅ Found {len(matches)} matching jobs!")
                    
                    for _, job in matches.iterrows():
                        score = round(job.get('match_score', 0) * 100, 1)
                        
                        if score >= 70:
                            score_color = "🟢"
                        elif score >= 50:
                            score_color = "🟡"
                        else:
                            score_color = "🔴"
                        
                        with st.container():
                            st.markdown(f"""
                            **🔹 {job['title']}** at **{job['company']}**  
                            {score_color} **Match: {score}%** | 📍 {job['location']} | 🕒 {job['experience']}  
                            🛠️ **Skills:** {job['skills'][:100]}...  
                            🔗 [Apply Now]({job['link']})
                            """)
                            st.divider()
                            
            except Exception as e:
                st.error(f"Error during matching: {e}")

elif user_skills and st.session_state.jobs_df.empty:
    st.warning("⚠️ No job data available. Please scrape jobs first or load existing data.")

st.header("🤖 Machine Learning Job Clustering")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔬 Train ML Model"):
        if not st.session_state.jobs_df.empty:
            with st.spinner("Training unsupervised clustering model..."):
                from clustering_model import JobClusteringModel
                
                model = JobClusteringModel(n_clusters=4)
                clustered_df, insights = model.train_model(st.session_state.jobs_df.copy())
                model.save_model()
                
                st.session_state.clustered_df = clustered_df
                st.session_state.cluster_insights = insights
                st.session_state.model_trained = True
                
                st.success("✅ ML Model trained and saved!")
        else:
            st.warning("Please load job data first")

with col2:
    if st.button("📂 Load Saved Model"):
        try:
            from clustering_model import JobClusteringModel
            model = JobClusteringModel.load_model()
            st.session_state.model_loaded = True
            st.success("✅ Model loaded successfully!")
        except Exception as e:
            st.error(f"❌ Error loading model: {e}")

with col3:
    if st.button("🔮 Predict Job Category"):
        if user_skills and 'model_loaded' in st.session_state:
            try:
                from clustering_model import JobClusteringModel
                model = JobClusteringModel.load_model()
                
                predicted_cluster = model.predict_cluster(user_skills)
                st.info(f"🎯 Your skills match: **Cluster {predicted_cluster}**")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Enter skills and load model first")

if 'cluster_insights' in st.session_state:
    st.subheader("📊 Discovered Job Categories")
    
    cluster_names = [f"📋 {info['name']}" for info in st.session_state.cluster_insights.values()]
    tabs = st.tabs(cluster_names)
    
    for i, (cluster_id, info) in enumerate(st.session_state.cluster_insights.items()):
        with tabs[i]:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.metric("Total Jobs", info['job_count'])
                st.write("**🛠️ Key Skills:**")
                for skill in info['top_skills'][:6]:
                    st.write(f"• {skill}")
            
            with col2:
                st.write("**🏢 Companies:**")
                for company in info['companies'][:3]:
                    st.write(f"• {company}")
                
                st.write("**💼 Sample Jobs:**")
                for job in info['sample_jobs'][:2]:
                    st.write(f"• {job}")

if 'clustered_df' in st.session_state and user_skills:
    if st.button("🎯 Find Jobs by ML Clusters", type="primary"):
        with st.spinner("Matching jobs using ML clusters..."):
            from clustering_model import JobClusteringModel
            
            try:
                model = JobClusteringModel.load_model()
                user_cluster = model.predict_cluster(user_skills)
                
                cluster_jobs = st.session_state.clustered_df[
                    st.session_state.clustered_df['cluster'] == user_cluster
                ]
                
                cluster_name = st.session_state.cluster_insights[user_cluster]['name']
                
                st.success(f"🎯 Found {len(cluster_jobs)} jobs in your category: **{cluster_name}**")
                
                for _, job in cluster_jobs.iterrows():
                    with st.container():
                        st.markdown(f"""
                        **🔹 {job['title']}** at **{job['company']}**  
                        🤖 **Cluster:** {cluster_name} | 📍 {job['location']} | 🕒 {job['experience']}  
                        🛠️ **Skills:** {job['skills'][:100]}...  
                        🔗 [Apply Now]({job['link']})
                        """)
                        st.divider()
                
            except Exception as e:
                st.error(f"Error in ML matching: {e}")

st.markdown("---")
st.markdown("*Built with Streamlit • Real job data only*")
