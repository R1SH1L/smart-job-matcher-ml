import schedule
import time
from datetime import datetime
from scraper import scrape_and_save_jobs
from clustering_model import JobClusteringModel
from data_handler import load_jobs_from_csv

class JobMonitor:
    """Simple daily job monitoring system"""
    
    def __init__(self):
        self.user_preferences = {
            "user1": {"clusters": [0, 1], "email": "user1@example.com"},
            "user2": {"clusters": [2, 3], "email": "user2@example.com"}
        }
    
    def daily_job_check(self):
        """Daily automated job checking"""
        print(f"🕒 Daily job check started at {datetime.now()}")
        
        # 1. Scrape new jobs
        try:
            new_jobs = scrape_and_save_jobs("machine learning engineer", pages=2)
            print(f"📊 Scraped {len(new_jobs)} new jobs")
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            return
        
        if new_jobs.empty:
            print("📄 No new jobs found today")
            return
        
        # 2. Load trained model and classify new jobs
        try:
            model = JobClusteringModel.load_model()
            
            classified_jobs = []
            for _, job in new_jobs.iterrows():
                cluster = model.predict_cluster(job['skills'])
                job_dict = job.to_dict()
                job_dict['cluster'] = cluster
                classified_jobs.append(job_dict)
            
            print(f"🤖 Classified {len(classified_jobs)} jobs")
            
        except Exception as e:
            print(f"❌ Classification error: {e}")
            return
        
        # 3. Check user alerts
        self.check_alerts(classified_jobs)
    
    def check_alerts(self, jobs):
        """Check if jobs match user preferences"""
        for job in jobs:
            cluster = job['cluster']
            
            for user_id, prefs in self.user_preferences.items():
                if cluster in prefs['clusters']:
                    self.send_alert(user_id, job)
    
    def send_alert(self, user_id, job):
        """Send alert to user (console output for demo)"""
        user_email = self.user_preferences[user_id]['email']
        print(f"🔔 ALERT for {user_id} ({user_email}):")
        print(f"   📋 {job['title']} at {job['company']}")
        print(f"   🛠️ Skills: {job['skills'][:50]}...")
        print(f"   🔗 {job['link']}")
        print()
    
    def start_monitoring(self):
        """Start daily monitoring (for demo, runs every 2 minutes)"""
        # For demo: run every 2 minutes instead of daily
        schedule.every(2).minutes.do(self.daily_job_check)
        
        print("⏰ Monitoring started! (Demo: checks every 2 minutes)")
        print("🔔 User preferences configured:")
        for user_id, prefs in self.user_preferences.items():
            print(f"   {user_id}: Clusters {prefs['clusters']}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            print("🛑 Monitoring stopped")

if __name__ == "__main__":
    monitor = JobMonitor()
    monitor.start_monitoring()