import schedule
import time
from datetime import datetime
from scraper import scrape_and_save_jobs
from clustering_model import JobClusteringModel
from data_handler import load_jobs_from_csv
import pandas as pd

class DailyJobMonitor:
    """Automated daily job monitoring system"""
    
    def __init__(self):
        self.model = None
        self.user_preferences = {}  # user_id: [preferred_clusters]
        
    def load_model(self):
        """Load trained clustering model"""
        try:
            self.model = JobClusteringModel.load_model()
            print("✅ Clustering model loaded")
        except:
            print("⚠️ No trained model found. Training new model...")
            self.train_initial_model()
    
    def train_initial_model(self):
        """Train model on existing data"""
        jobs_df = load_jobs_from_csv()
        if jobs_df.empty:
            print("❌ No jobs data for training. Please scrape jobs first.")
            return
        
        self.model = JobClusteringModel(n_clusters=5)
        jobs_df, insights = self.model.train_model(jobs_df)
        self.model.save_model()
        
        print("📊 Cluster Analysis:")
        for cluster_id, info in insights.items():
            print(f"  Cluster {cluster_id}: {info['name']} ({info['job_count']} jobs)")
    
    def daily_scrape_and_classify(self):
        """Daily automated scraping and classification"""
        print(f"🕒 Daily scrape started at {datetime.now()}")
        
        # Scrape new jobs
        keywords = ["software developer", "data scientist", "machine learning engineer"]
        new_jobs = []
        
        for keyword in keywords:
            try:
                jobs = scrape_and_save_jobs(keyword, pages=2)
                new_jobs.extend(jobs.to_dict('records'))
            except Exception as e:
                print(f"❌ Error scraping {keyword}: {e}")
        
        if not new_jobs:
            print("📄 No new jobs found")
            return
        
        # Classify new jobs
        classified_jobs = []
        for job in new_jobs:
            try:
                cluster = self.model.predict_cluster(job['skills'])
                job['cluster'] = cluster
                classified_jobs.append(job)
            except Exception as e:
                print(f"⚠️ Classification error: {e}")
        
        print(f"✅ Classified {len(classified_jobs)} new jobs")
        
        # Check user alerts
        self.check_user_alerts(classified_jobs)
    
    def check_user_alerts(self, new_jobs):
        """Check if new jobs match user preferences"""
        alerts = {}
        
        for job in new_jobs:
            cluster = job.get('cluster')
            for user_id, preferred_clusters in self.user_preferences.items():
                if cluster in preferred_clusters:
                    if user_id not in alerts:
                        alerts[user_id] = []
                    alerts[user_id].append(job)
        
        # Send alerts (implement email/notification logic here)
        for user_id, matching_jobs in alerts.items():
            self.send_alert(user_id, matching_jobs)
    
    def send_alert(self, user_id, jobs):
        """Send alert to user (placeholder for email/notification)"""
        print(f"🔔 ALERT for User {user_id}: {len(jobs)} new matching jobs!")
        for job in jobs:
            print(f"  • {job['title']} at {job['company']}")
    
    def add_user_preference(self, user_id, preferred_clusters):
        """Add user job category preferences"""
        self.user_preferences[user_id] = preferred_clusters
        print(f"✅ Preferences set for User {user_id}: Clusters {preferred_clusters}")
    
    def start_daily_monitoring(self):
        """Start the daily monitoring schedule"""
        # Schedule daily scraping at 9 AM
        schedule.every().day.at("09:00").do(self.daily_scrape_and_classify)
        
        print("⏰ Daily monitoring started. Will scrape jobs daily at 9:00 AM")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("🛑 Daily monitoring stopped")

# Usage
if __name__ == "__main__":
    monitor = DailyJobMonitor()
    monitor.load_model()
    
    # Add sample user preferences
    monitor.add_user_preference("user1", [0, 1])  # Interested in clusters 0 and 1
    monitor.add_user_preference("user2", [2, 3])  # Interested in clusters 2 and 3
    
    # Start monitoring
    monitor.start_daily_monitoring()