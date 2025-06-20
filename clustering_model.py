from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd
import joblib
import numpy as np

class JobClusteringModel:
    
    def __init__(self, n_clusters=4):  
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            max_features=50, 
            stop_words='english',
            ngram_range=(1, 2),  
            min_df=2 
        )
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.pca = PCA(n_components=2)
        self.is_trained = False
        
    def train_model(self, jobs_df):
        """Train clustering model on job skills"""
        print(f"🤖 Training clustering model on {len(jobs_df)} jobs...")
        
        skills_text = self.clean_skills_text(jobs_df['skills'])
        
        X = self.vectorizer.fit_transform(skills_text)
        print(f"📊 Feature matrix shape: {X.shape}")
        
        clusters = self.kmeans.fit_predict(X)
        
        jobs_df['cluster'] = clusters
        
        cluster_insights = self.analyze_clusters(jobs_df)
        
        self.is_trained = True
        print(f"✅ Model trained! Found {self.n_clusters} job categories")
        
        return jobs_df, cluster_insights
    
    def clean_skills_text(self, skills_input):
        if hasattr(skills_input, 'fillna'):
            skills_list = skills_input.fillna('')
        else:
            skills_list = skills_input
        
        cleaned_skills = []
        
        for skills in skills_list:
            skills_str = str(skills).lower()
            
            skills_str = skills_str.replace('aartificial', 'artificial')
            skills_str = skills_str.replace('machine learning techniques', 'machine learning')
            skills_str = skills_str.replace('data science techniques', 'data science')
            skills_str = skills_str.replace('programminng', 'programming')
            skills_str = skills_str.replace('teechniques', 'techniques')
            skills_str = skills_str.replace('kubernettes', 'kubernetes')
            
            skills_str = ' '.join(skills_str.split())
            
            cleaned_skills.append(skills_str)
        
        return cleaned_skills
    
    def predict_cluster(self, job_skills):
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        
        cleaned_skills = self.clean_skills_text([job_skills])
        skills_vector = self.vectorizer.transform(cleaned_skills)
        cluster = self.kmeans.predict(skills_vector)[0]
        return cluster
    
    def analyze_clusters(self, jobs_df):
        insights = {}
        
        for cluster_id in range(self.n_clusters):
            cluster_jobs = jobs_df[jobs_df['cluster'] == cluster_id]
            
            all_skills = []
            for skills in cluster_jobs['skills']:
                skills_list = [s.strip() for s in str(skills).split(',')]
                all_skills.extend(skills_list)
            
            skill_counts = {}
            for skill in all_skills:
                if skill and len(skill) > 2:
                    skill = skill.replace('Aartificial intelligence', 'Artificial Intelligence')
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            
            cluster_name = self.generate_cluster_name(top_skills, cluster_jobs['title'].tolist())
            
            insights[cluster_id] = {
                'name': cluster_name,
                'job_count': len(cluster_jobs),
                'top_skills': [skill for skill, count in top_skills],
                'sample_jobs': cluster_jobs['title'].head(3).tolist(),
                'companies': cluster_jobs['company'].unique().tolist()[:3]
            }
        
        return insights
    
    def generate_cluster_name(self, top_skills, job_titles):
        if not top_skills:
            return "General Jobs"
        
        skill_text = ' '.join([skill.lower() for skill, count in top_skills[:5]])
        title_text = ' '.join([title.lower() for title in job_titles[:5]])
        
        if any(keyword in skill_text for keyword in ['python', 'machine learning', 'data science', 'analytics']):
            return "Data Science & ML Engineering"
        elif any(keyword in skill_text for keyword in ['backend', 'api', 'java', 'spring']):
            return "Backend Development"
        elif any(keyword in skill_text for keyword in ['frontend', 'react', 'javascript', 'html']):
            return "Frontend Development"  
        elif any(keyword in skill_text for keyword in ['aws', 'docker', 'kubernetes', 'devops']):
            return "DevOps & Cloud Engineering"
        elif any(keyword in skill_text for keyword in ['design', 'ui', 'ux']):
            return "Design & Product"
        elif any(keyword in title_text for keyword in ['manager', 'product', 'lead']):
            return "Management & Leadership"
        else:
            primary_skill = top_skills[0][0]
            return f"{primary_skill} Specialist"
    
    def save_model(self, filepath='models/job_clustering_model.pkl'):
        import os
        os.makedirs('models', exist_ok=True)
        
        model_data = {
            'vectorizer': self.vectorizer,
            'kmeans': self.kmeans,
            'n_clusters': self.n_clusters,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        print(f"💾 Model saved to {filepath}")
    
    @classmethod
    def load_model(cls, filepath='models/job_clustering_model.pkl'):
        model_data = joblib.load(filepath)
        
        model = cls(n_clusters=model_data['n_clusters'])
        model.vectorizer = model_data['vectorizer']
        model.kmeans = model_data['kmeans']
        model.is_trained = model_data['is_trained']
        
        print(f"📂 Model loaded from {filepath}")
        return model
    
    def get_cluster_summary(self):
        if not self.is_trained:
            return "Model not trained yet"
        
        return f"Trained K-Means model with {self.n_clusters} clusters"