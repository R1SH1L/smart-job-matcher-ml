import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime
from data_handler import save_jobs_to_csv, load_jobs_from_csv

def scrape_and_save_jobs(keyword="software developer", pages=2, update_csv=True):
    print(f"🔍 Scraping '{keyword}' jobs...")
    
    df = scrape_jobs(keyword, pages)
    
    print(f"📊 DataFrame info:")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns) if not df.empty else 'No columns'}")
    print(f"  Empty: {df.empty}")
    
    if not df.empty:
        print("📋 Sample data:")
        print(df.head(2))
        
        if update_csv:
            df['scraped_at'] = datetime.now().isoformat()
            df['keyword'] = keyword
            
            print(f"📊 After adding metadata:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            
            from data_handler import save_jobs_to_csv
            save_jobs_to_csv(df, append=False)  
            
            print(f"✅ Jobs saved successfully!")
    else:
        print("❌ No jobs to save - scraping returned empty results")
    
    return df

def scrape_jobs(keyword="software developer", pages=2):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    base_url = "https://www.karkidi.com/Find-Jobs/{page}/all/India?search={query}"
    jobs_list = []

    print(f"🔍 Scraping Karkidi for '{keyword}' jobs...")

    for page in range(1, pages + 1):
        try:
            url = base_url.format(page=page, query=keyword.replace(' ', '%20'))
            print(f"📄 Scraping page {page}")
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Failed to get page {page}: Status {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.content, "html.parser")
            job_blocks = soup.find_all("div", class_="ads-details")
            print(f"🎯 Found {len(job_blocks)} job blocks on page {page}")
            
            for i, job in enumerate(job_blocks):
                try:
                    job_data = extract_job_data(job, url, i)
                    if job_data and is_valid_job(job_data):
                        jobs_list.append(job_data)
                        
                        if i < 3:  
                            print(f"✅ Job {len(jobs_list)}: {job_data['title']} at {job_data['company']}")
                    
                except Exception as e:
                    print(f"⚠️ Error parsing job {i+1}: {e}")
                    continue

            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"❌ Error scraping page {page}: {e}")
            continue

    print(f"🎉 Total valid jobs scraped: {len(jobs_list)}")
    
    if jobs_list:
        return pd.DataFrame(jobs_list)
    else:
        print("❌ No real jobs found")
        return pd.DataFrame()

def extract_job_data(job, url, index):
    title_elem = job.find("h4")
    title = title_elem.get_text(strip=True) if title_elem else None
    
    company_elem = job.find("a", href=lambda x: x and "Employer-Profile" in x)
    company = company_elem.get_text(strip=True) if company_elem else None
    
    location_elem = job.find("p")
    location = location_elem.get_text(strip=True) if location_elem else "Location Not Specified"
    
    experience_elem = job.find("p", class_="emp-exp")
    experience = experience_elem.get_text(strip=True) if experience_elem else "Experience Not Specified"
    
    key_skills_tag = job.find("span", string="Key Skills")
    if key_skills_tag:
        skills_elem = key_skills_tag.find_next("p")
        skills = skills_elem.get_text(strip=True) if skills_elem else ""
    else:
        skills = extract_skills_from_text(job.get_text())
    
    summary_tag = job.find("span", string="Summary")
    if summary_tag:
        summary_elem = summary_tag.find_next("p")
        summary = summary_elem.get_text(strip=True) if summary_elem else ""
    else:
        summary = "No summary available"
    
    link_elem = job.find("a", href=True)
    if link_elem:
        href = link_elem['href']
        link = href if href.startswith('http') else f"https://www.karkidi.com{href}"
    else:
        link = url
    
    if not title or not company:
        return None
    
    return {
        "title": clean_text(title),
        "company": clean_text(company),
        "location": clean_text(location),
        "experience": clean_text(experience),
        "summary": clean_text(summary),
        "skills": skills if skills else "Skills not specified",
        "link": link
    }

def is_valid_job(job_data):
    """Validate if job data looks legitimate"""
    if not job_data:
        return False
    
    title = job_data.get('title', '').lower()
    company = job_data.get('company', '').lower()
    
    invalid_keywords = [
        'filter by', 'toggle navigation', 'employer login', 'sign up',
        'forgot password', 'new clients', 'register now', 'job types'
    ]
    
    for keyword in invalid_keywords:
        if keyword in title or keyword in company:
            return False
    
    if len(job_data.get('title', '')) < 3 or len(job_data.get('company', '')) < 2:
        return False
    
    return True

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return "Not specified"
    
    text = str(text).strip()
    text = ' '.join(text.split())  
    
    unwanted = ['click here', 'read more', 'apply now', 'view details', 'learn more']
    for phrase in unwanted:
        text = text.replace(phrase, '')
    
    return text.strip()

def extract_skills_from_text(text):
    tech_keywords = [
        'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'HTML', 'CSS',
        'Django', 'Flask', 'Spring', 'Angular', 'Vue', 'MongoDB', 'PostgreSQL',
        'MySQL', 'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'Linux',
        'Machine Learning', 'Data Science', 'AI', 'REST', 'API', 'JSON',
        'C++', 'C#', '.NET', 'PHP', 'Laravel', 'Ruby', 'Go', 'Rust', 'GCP'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in tech_keywords:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    unique_skills = list(dict.fromkeys(found_skills))
    return ", ".join(unique_skills[:8]) if unique_skills else ""

def extract_all_skills(job_df):
    if job_df.empty:
        return []
    
    all_skills = set()
    priority_skills = [
        'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'HTML', 'CSS',
        'AWS', 'Docker', 'Kubernetes', 'Git', 'Machine Learning', 'Data Science',
        'Django', 'Flask', 'Spring Boot', 'Angular', 'Vue.js', 'MongoDB', 'PostgreSQL',
        'MySQL', 'Redis', 'Linux', 'Azure', 'GCP', 'DevOps', 'CI/CD', 'REST API',
        'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'TypeScript', 'PHP', 'Laravel'
    ]
    
    for _, row in job_df.iterrows():
        skills_text = str(row.get('skills', ''))
        for skill in priority_skills:
            if skill.lower() in skills_text.lower():
                all_skills.add(skill)
    
    skill_counts = {}
    for skill in all_skills:
        count = sum(1 for _, row in job_df.iterrows() 
                   if skill.lower() in str(row.get('skills', '')).lower())
        skill_counts[skill] = count
    
    sorted_skills = sorted(all_skills, key=lambda x: (-skill_counts[x], x))
    return sorted_skills[:25]
