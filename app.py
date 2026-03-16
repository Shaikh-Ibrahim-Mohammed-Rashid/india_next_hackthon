import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
import nltk
import numpy as np
import pdfplumber
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity

from domain_classifier import detect_domain
from skill_extractor import extract_skills, extract_all_skills, get_skill_score

nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

app = Flask(__name__)
CORS(app, supports_credentials=True)

ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_DIR = os.path.join(ROOT, 'model')

TFIDF_DOMAINS = {"INFORMATION-TECHNOLOGY"}

JOB_SITES = [
    ("Google Jobs",   "https://www.google.com/search?q={q}+jobs+india"),
    ("Indeed",        "https://in.indeed.com/jobs?q={q}&l=India"),
    ("Naukri",        "https://www.naukri.com/{s}-jobs"),
    ("Internshala",   "https://internshala.com/jobs/{s}-jobs"),
    ("Apna",          "https://apna.co/jobs?q={q}"),
    ("Shine",         "https://www.shine.com/job-search/{s}-jobs"),
    ("TimesJobs",     "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={q}"),
    ("Glassdoor",     "https://www.glassdoor.co.in/Job/{s}-jobs-SRCH_KO0,20.htm"),
    ("Freshersworld", "https://www.freshersworld.com/jobs/jobsearch/{s}-jobs"),
    ("Foundit",       "https://www.foundit.in/srp/results?query={q}&location=India"),
]

def build_links(role):
    q = role.replace(" ", "+")
    s = role.lower().replace(" ", "-")
    return [
        {"name": name, "url": url.replace("{q}", q).replace("{s}", s)}
        for name, url in JOB_SITES
    ]

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z ]', '', text)
    return " ".join(w for w in text.split() if w not in stop_words)

def predict(resume_text, domain):
    if domain in TFIDF_DOMAINS:
        vectorizer  = pickle.load(open(os.path.join(MODEL_DIR, "vectorizer.pkl"),  "rb"))
        job_vectors = pickle.load(open(os.path.join(MODEL_DIR, "job_vectors.pkl"), "rb"))
        jobs        = pickle.load(open(os.path.join(MODEL_DIR, "jobs.pkl"),        "rb"))
        vec         = vectorizer.transform([clean_text(resume_text)])
        sim         = cosine_similarity(vec, job_vectors).flatten()
        top5        = sim.argsort()[::-1][:5]
        return [(jobs.iloc[i]["Job Title"], round(float(sim[i]) * 100, 2)) for i in top5]
    else:
        vectorizer = pickle.load(open(os.path.join(MODEL_DIR, "resume_vectorizer.pkl"), "rb"))
        model      = pickle.load(open(os.path.join(MODEL_DIR, "resume_classifier.pkl"), "rb"))
        vec        = vectorizer.transform([clean_text(resume_text)])
        probs      = model.predict_proba(vec)[0]
        top5       = np.argsort(probs)[::-1][:5]
        return [(model.classes_[i], round(probs[i] * 100, 2)) for i in top5]


@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Resume Analyzer API running", "version": "2.0"})


@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files accepted"}), 400

    temp_path = os.path.join(ROOT, "uploads", f"_temp_{file.filename}")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    file.save(temp_path)

    try:
        text = ""
        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + " "
    except Exception as e:
        return jsonify({"error": f"PDF read error: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    if not text.strip():
        return jsonify({"error": "Could not extract text. PDF may be scanned/image-based."}), 400

    domain      = detect_domain(text)
    top5        = predict(text, domain)
    skills      = extract_skills(text, domain)
    all_skills  = extract_all_skills(text)
    skill_score = get_skill_score(text, domain)
    top_role    = top5[0][0]
    links       = build_links(top_role)

    clean_skills = [s for s in skills if s != "No specific skills detected"]

    cross_domain = {
        d: v for d, v in list(all_skills.items())[:3] if d != domain
    }

    return jsonify({
        "domain":       domain,
        "top5":         [{"role": r, "confidence": c} for r, c in top5],
        "skills":       clean_skills,
        "skill_score":  skill_score,
        "cross_skills": cross_domain,
        "links":        links,
        "top_role":     top_role,
        "char_count":   len(text)
    })


if __name__ == "__main__":
    print(f"\n Resume Analyzer API v2.0")
    print(f"   Root      : {ROOT}")
    print(f"   Model dir : {MODEL_DIR}")
    print(f"   Running at: http://localhost:5000\n")
    app.run(debug=True, port=5000, host="0.0.0.0")