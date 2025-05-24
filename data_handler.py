"""Handle CSV operations for job data"""

import pandas as pd
import os
from datetime import datetime

CSV_FILE = "data/jobs.csv"

def save_jobs_to_csv(df, append=True):
    """Save or update jobs in CSV file"""
    print(f"💾 Attempting to save DataFrame:")
    print(f"  Shape: {df.shape}")
    print(f"  Empty: {df.empty}")
    print(f"  Columns: {list(df.columns) if not df.empty else 'No columns'}")
    
    if df.empty:
        print("⚠️ No data to save - DataFrame is empty")
        return False
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    try:
        if append and os.path.exists(CSV_FILE):
            # Check if existing file is valid
            try:
                existing_df = pd.read_csv(CSV_FILE)
                print(f"📋 Found existing CSV with {len(existing_df)} jobs")
                
                # Remove duplicates based on title + company
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df = combined_df.drop_duplicates(
                    subset=['title', 'company'], 
                    keep='last'  # Keep latest version
                )
                
                combined_df.to_csv(CSV_FILE, index=False)
                print(f"📊 Updated CSV: {len(combined_df)} total jobs")
                
            except pd.errors.EmptyDataError:
                print("📄 Existing CSV is empty, creating new file...")
                df.to_csv(CSV_FILE, index=False)
                print(f"💾 Created new CSV: {len(df)} jobs saved")
                
        else:
            # Create new file
            print(f"💾 Creating new CSV file...")
            df.to_csv(CSV_FILE, index=False)
            print(f"💾 Successfully saved {len(df)} jobs to {CSV_FILE}")
            
            # Verify the file was created correctly
            verify_df = pd.read_csv(CSV_FILE)
            print(f"✅ Verification: {len(verify_df)} jobs loaded back from CSV")
            
        return True
            
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")
        print(f"❌ Error type: {type(e)}")
        return False

def load_jobs_from_csv():
    """Load jobs from CSV file"""
    if not os.path.exists(CSV_FILE):
        print("📄 No existing CSV found")
        return pd.DataFrame()
    
    try:
        # Check if file is empty
        if os.path.getsize(CSV_FILE) == 0:
            print("📄 CSV file exists but is empty")
            return pd.DataFrame()
        
        df = pd.read_csv(CSV_FILE)
        print(f"📋 Loaded {len(df)} jobs from CSV")
        return df
        
    except pd.errors.EmptyDataError:
        print("📄 CSV file exists but has no data/columns")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return pd.DataFrame()

def get_csv_stats():
    """Get CSV file statistics"""
    if not os.path.exists(CSV_FILE):
        return {"exists": False}
    
    try:
        # Check file size first
        if os.path.getsize(CSV_FILE) == 0:
            return {"exists": True, "empty": True}
        
        df = pd.read_csv(CSV_FILE)
        file_time = os.path.getmtime(CSV_FILE)
        last_updated = datetime.fromtimestamp(file_time)
        
        return {
            "exists": True,
            "empty": False,
            "total_jobs": len(df),
            "companies": df['company'].nunique() if not df.empty else 0,
            "last_updated": last_updated.strftime("%Y-%m-%d %H:%M"),
            "top_skills": get_top_skills(df) if not df.empty else []
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}

def get_top_skills(df, top_n=10):
    """Get most common skills from CSV data"""
    if df.empty:
        return []
    
    all_skills = []
    for skills_text in df['skills'].fillna(''):
        skills_list = [s.strip() for s in str(skills_text).split(',')]
        all_skills.extend([s for s in skills_list if s and len(s) > 2])
    
    # Count occurrences
    skill_counts = {}
    for skill in all_skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # Return top skills
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    return [skill for skill, count in sorted_skills[:top_n]]

# Helper function to manually create a test CSV
def create_test_csv_from_scraped_data():
    """Create test CSV from your working scraper"""
    from scraper import scrape_jobs
    
    print("🔧 Creating test CSV from fresh scrape...")
    df = scrape_jobs("software developer", pages=1)
    
    if not df.empty:
        # Add required columns
        df['scraped_at'] = datetime.now().isoformat()
        df['keyword'] = "software developer"
        
        # Force save to CSV
        os.makedirs("data", exist_ok=True)
        df.to_csv(CSV_FILE, index=False)
        print(f"✅ Force-saved {len(df)} jobs to CSV")
        
        # Verify
        test_load = pd.read_csv(CSV_FILE)
        print(f"✅ Verified: {len(test_load)} jobs loaded back")
        return True
    else:
        print("❌ No data to save")
        return False