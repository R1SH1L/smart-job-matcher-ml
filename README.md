# Smart Job Matcher with ML Clustering

A machine learning-powered job matching system that scrapes job postings and categorizes them using K-Means clustering algorithms.

## Features

- Job scraping from Karkidi.com
- K-Means clustering for job categorization
- Streamlit web interface
- Model persistence
- Daily automation

## Technology Stack

- **Frontend**: Streamlit
- **Machine Learning**: scikit-learn, pandas, numpy
- **Web Scraping**: BeautifulSoup, requests
- **Data Storage**: CSV, joblib

## Project Structure

```
smart-job-matcher/
├── data/
│   └── jobs.csv
├── models/
│   └── job_clustering_model.pkl
├── src/
│   ├── app.py
│   ├── scraper.py
│   ├── clustering_model.py
│   ├── matcher.py
│   ├── data_handler.py
│   └── daily_automation.py
├── requirements.txt
└── README.md
```

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run src/app.py
   ```

## Usage

1. **Scrape Jobs**: Use the interface to scrape job listings
2. **Train Model**: Apply K-Means clustering to categorize jobs
3. **Match Jobs**: Get job recommendations based on skills
4. **Automate**: Set up daily job monitoring

## Requirements

- Python 3.8+
- Internet connection for scraping