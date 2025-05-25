import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def match_jobs(user_skills, job_df):
    if job_df.empty:
        return pd.DataFrame()
    
    job_df = job_df.copy()
    
    job_df['skills'] = job_df['skills'].fillna('').apply(preprocess_skills)
    user_skills_processed = preprocess_skills(user_skills)
    
    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),  
        max_features=1000,
        lowercase=True
    )
    
    try:
        all_skills = job_df['skills'].tolist() + [user_skills_processed]
        tfidf_matrix = vectorizer.fit_transform(all_skills)
        
        user_vector = tfidf_matrix[-1]
        job_vectors = tfidf_matrix[:-1]
        
        similarities = cosine_similarity(user_vector, job_vectors).flatten()
        job_df['match_score'] = similarities
        
        matched_jobs = job_df[job_df['match_score'] > 0.01].sort_values(
            by='match_score', ascending=False
        ).head(10)
        
        return matched_jobs
        
    except Exception as e:
        print(f"Error in matching: {e}")
        job_df['match_score'] = 0.0
        return job_df.head(10)

def preprocess_skills(text):
    if pd.isna(text) or not text:
        return ""
    
    text = str(text).lower()
    
    text = re.sub(r'[^\w\s]', ' ', text)
    
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()
