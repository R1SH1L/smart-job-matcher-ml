# Smart Job Matcher with ML Clustering

An intelligent job matching system that scrapes job postings from Karkidi.com and categorizes them using machine learning clustering.

## Features

- Web scraping from Karkidi.com
- Machine learning job categorization using K-Means clustering
- Interactive web interface with Streamlit
- Job matching based on user skills
- Automated daily monitoring

## Technology Stack

- **Frontend:** Streamlit
- **ML:** scikit-learn, pandas, numpy
- **Web Scraping:** BeautifulSoup, requests
- **Storage:** CSV files, joblib

## Project Structure

```
smart-job-matcher/
├── data/
│   └── jobs.csv
├── models/
│   └── job_clustering_model.pkl
├── app.py
├── scraper.py
├── clustering_model.py
├── matcher.py
├── data_handler.py
├── daily_automation.py
└── requirements.txt
```

## Installation

```bash
git clone https://github.com/R1SH1L/smart-job-matcher-ml.git
cd smart-job-matcher-ml
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## How It Works

1. **Scrape Jobs:** Enter keywords and scrape job listings
2. **Train Model:** Use K-Means clustering to categorize jobs
3. **Match Jobs:** Enter your skills to find relevant jobs
4. **Monitor:** Set up automated daily job monitoring

## Requirements Met

- Web scraping from Karkidi.com
- Unsupervised machine learning clustering
- Model persistence
- Daily automation
- User alerts