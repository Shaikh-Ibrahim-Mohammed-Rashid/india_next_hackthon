import pandas as pd
import re
import pickle
import nltk
import os
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

jobs = pd.read_csv("JobsDatasetProcessed.csv")

jobs['combined'] = (
    jobs['Job Title'].fillna('') + " " +
    jobs['Description'].fillna('') + " " +
    jobs['IT Skills'].fillna('') + " " +
    jobs['Soft Skills'].fillna('')
)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z ]', '', text)
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words)

jobs['cleaned'] = jobs['combined'].apply(clean_text)

vectorizer = TfidfVectorizer(max_features=5000)
job_vectors = vectorizer.fit_transform(jobs['cleaned'])

os.makedirs("model", exist_ok=True)
pickle.dump(vectorizer,  open("model/vectorizer.pkl", "wb"))
pickle.dump(job_vectors, open("model/job_vectors.pkl", "wb"))
pickle.dump(jobs,        open("model/jobs.pkl", "wb"))

print("✅ IT Jobs model trained and saved!")