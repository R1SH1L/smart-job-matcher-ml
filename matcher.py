import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def match_jobs(user_skills, job_df):
    """Match user skills with job requirements using TF-IDF and cosine similarity"""
    if job_df.empty:
        return pd.DataFrame()
    
    # Make a copy to avoid modifying the original dataframe
    job_df = job_df.copy()
    
    # Preprocess skills text
    job_df['skills'] = job_df['skills'].fillna('').apply(preprocess_skills)
    user_skills_processed = preprocess_skills(user_skills)
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),  # Include single words and bigrams
        max_features=1000,
        lowercase=True
    )
    
    try:
        # Combine job skills and user skills for vectorization
        all_skills = job_df['skills'].tolist() + [user_skills_processed]
        tfidf_matrix = vectorizer.fit_transform(all_skills)
        
        # Get user vector (last one) and job vectors (all others)
        user_vector = tfidf_matrix[-1]
        job_vectors = tfidf_matrix[:-1]
        
        # Calculate cosine similarity
        similarities = cosine_similarity(user_vector, job_vectors).flatten()
        job_df['match_score'] = similarities
        
        # Filter out very low matches and return top matches
        matched_jobs = job_df[job_df['match_score'] > 0.01].sort_values(
            by='match_score', ascending=False
        ).head(10)
        
        return matched_jobs
        
    except Exception as e:
        print(f"Error in matching: {e}")
        # Return jobs without scores as fallback
        job_df['match_score'] = 0.0
        return job_df.head(10)

def preprocess_skills(text):
    """Clean and preprocess skills text for better matching"""
    if pd.isna(text) or not text:
        return ""
    
    # Convert to string and lowercase
    text = str(text).lower()
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    return text.strip()
