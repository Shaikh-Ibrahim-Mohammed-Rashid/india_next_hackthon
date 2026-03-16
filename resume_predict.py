import pickle
import re
import nltk
import webbrowser
import numpy as np
import pdfplumber
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity

from domain_classifier import detect_domain
from skill_extractor import extract_skills, extract_all_skills

nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

TFIDF_DOMAINS = {"INFORMATION-TECHNOLOGY"}

JOB_SEARCH_SITES = [
    ("Google Jobs",    "https://www.google.com/search?q={query}+jobs"),
    ("Indeed",         "https://in.indeed.com/jobs?q={query}"),
    ("Naukri",         "https://www.naukri.com/{slug}-jobs"),
    ("Shine",          "https://www.shine.com/job-search/{slug}-jobs"),
    ("TimesJobs",      "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={query}"),
]

def build_job_links(role):
    query = role.replace(" ", "+")
    slug  = role.lower().replace(" ", "-")
    return [
        (name, url.replace("{query}", query).replace("{slug}", slug))
        for name, url in JOB_SEARCH_SITES
    ]

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + " "
    except Exception as e:
        print(f"❌ PDF error: {e}")
    return text.strip()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z ]', '', text)
    return " ".join(w for w in text.split() if w not in stop_words)

def predict_with_classifier(resume_text):
    vectorizer = pickle.load(open("model/resume_vectorizer.pkl", "rb"))
    model      = pickle.load(open("model/resume_classifier.pkl", "rb"))
    vec        = vectorizer.transform([clean_text(resume_text)])
    probs      = model.predict_proba(vec)[0]
    top3       = np.argsort(probs)[::-1][:3]
    return [(model.classes_[i], round(probs[i]*100, 2)) for i in top3]

def predict_with_tfidf(resume_text):
    vectorizer  = pickle.load(open("model/vectorizer.pkl",  "rb"))
    job_vectors = pickle.load(open("model/job_vectors.pkl", "rb"))
    jobs        = pickle.load(open("model/jobs.pkl",        "rb"))
    vec         = vectorizer.transform([clean_text(resume_text)])
    sim         = cosine_similarity(vec, job_vectors).flatten()
    top3        = sim.argsort()[::-1][:3]
    return [(jobs.iloc[i]["Job Title"], round(float(sim[i])*100, 2)) for i in top3]

def main():
    print("\n🚀 Resume Analyzer")
    pdf_path    = input("Enter resume PDF path: ").strip().strip('"')
    resume_text = extract_text_from_pdf(pdf_path)

    if not resume_text:
        print("❌ Could not extract text.")
        return

    domain = detect_domain(resume_text)
    print(f"✅ Domain: {domain}")

    top3 = predict_with_tfidf(resume_text) if domain in TFIDF_DOMAINS \
           else predict_with_classifier(resume_text)

    top_role = top3[0][0]
    links    = build_job_links(top_role)

    print(f"\n🏆 Top Role: {top_role}")
    print(f"🌐 Opening top 5 job search sites for: {top_role}\n")

    for name, url in links:
        print(f"  → {name}: {url}")
        webbrowser.open(url)

if __name__ == "__main__":
    main()