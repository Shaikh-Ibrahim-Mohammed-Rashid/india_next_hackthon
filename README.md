<div align="center">

# DOMinator.ai

### AI-Powered Student Guidance & Fraud Detection Platform

**india next hackthon Hackathon — Team THE DOMinators**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3%2B-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5.2-orange?style=for-the-badge&logo=scikit-learn)](https://scikit-learn.org/)
[![Mistral AI](https://img.shields.io/badge/Mistral_AI-LLM-purple?style=for-the-badge)](https://mistral.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

> **DOMinator.ai** is a unified, cyberpunk-themed web platform that solves two critical problems facing modern students:  
> **(1)** Lack of intelligent, data-driven guidance for college admissions in Maharashtra  
> **(2)** Rising scams in the form of fake internships and fraudulent job postings

---

</div>

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Proposed Solution](#3-proposed-solution)
4. [Key Features](#4-key-features)
5. [System Architecture](#5-system-architecture)
6. [Technologies Used](#6-technologies-used)
7. [Modules Explanation](#7-modules-explanation)
8. [Dataset Information](#8-dataset-information)
9. [Installation Guide](#9-installation-guide)
10. [How to Run the Project](#10-how-to-run-the-project)
11. [Usage Instructions](#11-usage-instructions)
12. [Project Workflow](#12-project-workflow)
13. [Folder Structure](#13-folder-structure)
14. [Future Improvements](#14-future-improvements)
15. [Contributors](#15-contributors)
16. [License](#16-license)

---

## 1. Project Overview

**DOMinator.ai** is a full-stack AI-powered web application built with **Flask** that merges two intelligent tools into a single authenticated platform:

| Sub-System | Purpose |
|---|---|
| **DigiPath AI** | Predicts Diploma-to-Engineering (DSE) admission college cutoffs and counsels students on their admission chances |
| **SnifTern.ai** | Detects fake/scam internship and job postings using a multi-layer AI pipeline (ML + LLM + SERP) |
| **MHT-CET Predictor** | Predicts First Year Engineering (FYE) admission eligibility based on MHT-CET cutoff data |
| **College Search** | Provides searchable access to a detailed college database for Maharashtra |
| **Analytics Dashboard** | Real-time visualizations and trend analysis of fraud detection results |

The entire application is wrapped in an immersive **cyberpunk UI** with role-based plan tiers (Free / Pro), user authentication, and a unified services dashboard.

---

## 2. Problem Statement

Students in Maharashtra — particularly diploma holders and 12th-grade students — face two critical, underserved challenges:

### Challenge 1: College Admission Blindness
- Students applying under **DSE (Direct Second Year Engineering)** or **MHT-CET** routes have no reliable tool to predict their admission chances based on real cutoff trends.
- Existing data is scattered, outdated, or not AI-powered.
- Students waste time applying to unachievable colleges or miss suitable ones.

### Challenge 2: Rising Internship and Job Scams
- The number of **fake internship and job postings** targeting students has increased dramatically.
- Scammers lure students with promises of remote work, certificates, and high pay — only to collect money or personal data.
- Students lack the tools or knowledge to identify such fraudulent opportunities before it is too late.

---

## 3. Proposed Solution

DOMinator.ai addresses both challenges in a single, integrated platform:

### For College Admissions — DigiPath AI & MHT-CET Predictor
- Uses **historical cutoff data** from 2024 and 2025 CAP rounds.
- Offers **4 AI prediction models** (AI Trend, Weighted, Safe Mode, Lucky Mode) to forecast cutoffs.
- Students input their percentage, preferred course, and category to get a ranked list of eligible colleges with their admission probability.

### For Scam Detection — SnifTern.ai
- A **3-level verification pipeline**:
  1. **Level 1 (ML)** — TF-IDF + Logistic Regression model trained on real fake job data.
  2. **Level 2 (LLM)** — Mistral AI (`mistral-large-latest`) for intelligent contextual analysis.
  3. **Level 3 (SERP)** — Google Search (via SERP API) to verify company reputation in real-world web results.
- Accepts input as raw text, a PDF upload, or a URL.
- Returns a detailed verdict: **LEGITIMATE / FAKE / SUSPICIOUS** with confidence score, red flags, green flags, and source links.

---

## 4. Key Features

### Authentication & Access Control
- Secure session-based login system.
- Plan selection (Free / Pro) before accessing services.
- All service routes are protected; unauthorized access is redirected.

### DigiPath AI (DSE Admission Module)
- Predict cutoffs for Diploma-to-SE admission (DSE).
- 4 prediction models: AI Trend, Weighted Recent, Safe, Lucky.
- Admits filter by Course, Category, and Marks.
- Interactive visualizations: Cutoff Trend Lines, Model Comparison Bar Chart, Success Probability Donut Chart.

### MHT-CET Predictor (FYE Admission Module)
- Predict college admissions for First Year Engineering via MHT-CET.
- Supports Current Data mode and Forecast (ML model) mode.
- City, Branch, and Category filters.
- Auto-classifies colleges as SAFE, MODERATE, or RISKY based on gap analysis.

### SnifTern.ai (Scam Detection Module)
- Multi-input support: paste text, upload a PDF, or submit a URL.
- 3-level AI pipeline: ML + LLM + Web Search.
- Detailed output: verdict, confidence score, red flags, green flags, recommendation, risk level.
- Pattern detection for 10+ fraud categories (payment for certificate, urgent hiring, suspicious salary, etc.).
- Company reputation search powered by SERP API with live source links.

### College Database Search
- Instant search by College ID or Name.
- Displays college details: branches offered, intake capacity, city, and more.

### Analytics Dashboard
- Real-time charts of detection trends, fraud rate, pattern frequency, and source distribution.
- Industry-wise and location-wise fraud insights.
- Recommendations generated from aggregated data.

### Cyberpunk UI
- Full dark-theme interface styled with `Orbitron` and `JetBrains Mono` fonts.
- Responsive layout with a persistent sidebar navigation.
- Dynamic chart rendering (Matplotlib → Base64 PNG embedded in HTML).

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      DOMinator.ai                           │
│                   (Flask Web Application)                   │
├────────────────────┬────────────────────────────────────────┤
│   STUDENT MODULE   │          FRAUD DETECTION MODULE        │
│                    │                                        │
│  ┌─────────────┐   │   ┌──────────────────────────────────┐ │
│  │ DigiPath AI │   │   │          SnifTern.ai              │ │
│  │  (DSE CAP)  │   │   │                                  │ │
│  └──────┬──────┘   │   │  Input: Text / PDF / URL         │ │
│         │          │   │         │                        │ │
│  ┌──────▼──────┐   │   │  ┌──────▼──────────────────────┐ │ │
│  │  MHT-CET   │   │   │  │ Level 1: ML Classification   │ │ │
│  │  Predictor  │   │   │  │ TF-IDF + Logistic Regression │ │ │
│  └──────┬──────┘   │   │  └──────────────┬───────────────┘ │ │
│         │          │   │                 │                  │ │
│  ┌──────▼──────┐   │   │  ┌──────────────▼───────────────┐ │ │
│  │  College   │   │   │  │ Level 2: LLM Verification    │ │ │
│  │  Database  │   │   │  │ Mistral AI (mistral-large)   │ │ │
│  └────────────┘   │   │  └──────────────┬───────────────┘ │ │
│                    │   │                 │                  │ │
│                    │   │  ┌──────────────▼───────────────┐ │ │
│                    │   │  │ Level 3: Web Verification    │ │ │
│                    │   │  │ SERP API (Google Search)     │ │ │
│                    │   │  └──────────────┬───────────────┘ │ │
│                    │   │                 │                  │ │
│                    │   │         Final Verdict             │ │
│                    │   └──────────────────────────────────┘ │
├────────────────────┴────────────────────────────────────────┤
│              Analytics Dashboard (Plotly + Matplotlib)       │
├─────────────────────────────────────────────────────────────┤
│    Auth Layer → Login → Plan Selection → Services           │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Technologies Used

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.9+, Flask 2.3+ | Web framework, routing, session management |
| **ML Model** | scikit-learn 1.5.2 | TF-IDF vectorizer + Logistic Regression for scam classification |
| **LLM** | Mistral AI (`mistral-large-latest`) | Level 2 contextual verification |
| **Web Search** | SERP API (Google Search) | Level 3 real-world company reputation check |
| **Data Processing** | Pandas, NumPy | Data loading, filtering, and prediction calculations |
| **Visualization** | Matplotlib, Seaborn, Plotly | Charts and graphs for insights |
| **PDF Handling** | PyPDF2, pdf2image | PDF text extraction |
| **OCR** | Tesseract OCR (pytesseract, Pillow) | Image-to-text from scanned documents |
| **Web Scraping** | BeautifulSoup4, Requests | URL-based job posting scraping |
| **Frontend** | Bootstrap 5, Font Awesome, Vanilla JS | Responsive UI |
| **Fonts** | Orbitron, JetBrains Mono | Cyberpunk-style typography |

---

## 7. Modules Explanation

### `app.py` — Main Application Entry Point
The central Flask application file. Registers all routes, initializes components, and manages the request/response lifecycle.

- Loads DigiPath diploma data (`final_diploma_cleaned.csv`, `old_data.csv`) and college database on startup.
- Lazy-loads MHT-CET data (`data/fe_2024.csv`, `data/fe_2025.csv`) only when the CET route is first accessed.
- Manages user sessions, plan selection, and cross-module navigation.
- Converts Matplotlib figures to Base64-encoded PNG strings for inline HTML rendering.

**Key Routes:**

| Route | Method | Description |
|---|---|---|
| `/` | GET | Landing / Home page |
| `/login` | GET, POST | User authentication |
| `/pricing` | GET | Plan selection page |
| `/services` | GET | Main dashboard with sidebar navigation |
| `/digipath` | GET, POST | DSE Admission Predictor |
| `/cet` | GET, POST | MHT-CET FYE Admission Predictor |
| `/job` | GET | Scam Job/Internship Detector UI |
| `/company` | GET | Company Reputation Checker UI |
| `/database` | GET | College Database Search UI |
| `/analytics` | GET | Analytics Dashboard |
| `/detect` | POST (API) | Core scam detection endpoint |
| `/search_company` | POST (API) | Company reputation search |
| `/analyze_pdf` | POST (API) | PDF upload + analysis |
| `/analyze_url` | POST (API) | URL scraping + analysis |
| `/api/search-college` | POST (API) | College search query |
| `/api/analytics/dashboard` | GET (API) | Analytics data for dashboard |

---

### `enhanced_prediction_utils.py` — ML Scam Predictor (Level 1)
The `EnhancedFakeInternshipPredictor` class wraps the trained TF-IDF + Logistic Regression model.

- Loads `model/fake_job_model.pkl` and `model/tfidf_vectorizer.pkl`.
- Runs rule-based **pattern matching** across 10+ fraud categories before the ML model inference.
- Pattern categories include: `certificate_payment`, `urgent_opportunity`, `suspicious_payment`, `no_experience_required`, `virtual_internship_suspicious`, and more.
- Returns a structured result with `result`, `confidence_score`, `pattern_matches`, and `risk_level`.

---

### `llm_verification.py` — LLM Verifier (Level 2)
The `LLMVerifier` class uses **Mistral AI** to perform intelligent semantic verification of a job posting.

- Uses `mistral-large-latest` model via the `mistralai` Python SDK.
- Sends both the job text and the Level-1 ML result to the LLM for contextual analysis.
- The LLM returns a structured JSON verdict containing: `status`, `confidence_percentage`, `red_flags`, `green_flags`, `keywords`, and `recommendation`.
- Includes a fallback mechanism if the API is unavailable.
- Implements retry logic (up to 3 attempts) for resilient API calls.

---

### `serp_api_utils.py` — Web Verification (Level 3)
The `SERPAPIVerifier` class verifies company legitimacy using real-time Google Search results.

- Issues up to 10 targeted search queries per company (legitimacy, Glassdoor reviews, LinkedIn, BBB, fraud reports, etc.).
- Aggregates and deduplicates search results.
- Builds a `reputation_score` based on the presence of positive signals (official website, reviews, LinkedIn) vs negative signals (scam reports, FTC complaints, phishing warnings).
- Returns `source_links`, `scam_indicators`, `legitimate_indicators`, `warnings`, and a final `recommendation`.
- Leverages `Mistral AI` optionally for deeper AI-powered analysis of the search results.

---

### `analytics_dashboard.py` — Analytics Engine
The `AnalyticsDashboard` class aggregates all analysis results in memory and generates comprehensive reports.

- Tracks every detection result with timestamp, fraud classification, confidence score, company, industry, and location.
- Generates: summary metrics, fraud trends, pattern frequency analysis, industry insights, location insights, temporal trends, source distribution, and confidence distribution.
- Creates Plotly and Matplotlib visualizations embedded in the analytics page.
- Auto-generates data-driven recommendations.

---

### `train_model.py` — Model Training Script
Standalone script to train the ML scam detection model from scratch.

- Loads a labeled job posting dataset (CSV with `title`, `company_profile`, `description`, and `fraudulent` columns).
- Preprocesses text using `preprocess_text()`.
- Trains a `TfidfVectorizer` (3,000 features, English stop words, unigrams) + `LogisticRegression`.
- Evaluates with `classification_report` and saves model artifacts to `model/` using `joblib`.

**Usage:**
```bash
python train_model.py
```

---

### `preprocessing.py` — Text Preprocessing Utilities
Provides `preprocess_text()` and `clean_extracted_text()` helper functions.

- Decodes HTML entities, strips HTML tags (via BeautifulSoup), lowercases, and removes special characters.
- Used by both the model training pipeline and the live prediction pipeline to ensure consistent text normalization.

---

### `pdf_handler.py` — PDF & OCR Handler
The `PDFHandler` class extracts text from uploaded PDF files (offer letters, JD documents).

- **Primary method**: Direct text extraction via `PyPDF2` for text-based PDFs.
- **Fallback method**: OCR via `pdf2image` + `pytesseract` for scanned/image-based PDFs.
- Auto-configures Tesseract path on Windows.
- Enforces a 10 MB file size limit.

---

### `scraping_utils.py` — Web Scraping Utilities
Provides `extract_text_from_url()` and `is_valid_url()` for processing job posting URLs.

- Mimics a real browser with realistic HTTP headers.
- Strips non-content elements (nav, footer, scripts).
- Tries common content selectors (`main`, `article`, `.job-description`) before falling back to full `<body>` extraction.
- Applies respectful rate-limiting with random delays.

---

### `ocr_utils.py` — OCR Utilities
Standalone OCR helper using `pytesseract` and `Pillow`.

- `extract_text_from_image()` accepts file objects or paths.
- Validates Tesseract installation before running.
- Cleans extracted text for downstream processing.

---

### `blockchain_verification.py` — Blockchain Verification (Experimental)
The `BlockchainVerification` class provides a simulated immutable verification record for job postings and company credentials.

- Creates SHA-256 hashed blocks chaining job verification data.
- Runs automated checks (contact info, salary range, company website, description length, etc.).
- Assigns a `verification_score`; postings above 70% are marked as verified.
- Currently used as a verification audit trail component.

---

### `resume_analyzer.py` — Resume Analyzer (Experimental)
The `ResumeAnalyzer` class provides skill-matching and red-flag detection when analyzing a resume against a job posting.

- Extracts skills, experience, and education from resume text using regex and keyword matching.
- Compares against job requirements for a `compatibility_score`.
- Detects suspicious patterns (unrealistic claims, missing contact info, date inconsistencies).
- Uses `spacy` for NLP-based information extraction.

---

## 8. Dataset Information

| File | Description |
|---|---|
| `final_diploma_cleaned.csv` | Diploma-to-SE (DSE) Round 2 cutoff data for Maharashtra engineering colleges. Contains: `College Code`, `College Name`, `Course Name`, `Category`, `Percent` (R2). |
| `old_data.csv` | DSE Round 1 historical cutoff data. Used as baseline for trend calculations. |
| `detailed_college_database.csv` | Enriched institution database with branch-wise intake, city, accreditation, and other metadata. Used by the College Search module. |
| `data/fe_2024.csv` | MHT-CET First Year Engineering cutoff data for 2024. Contains: `College Name`, `City`, `Branch`, `Category`, `Cutoff`. |
| `data/fe_2025.csv` | MHT-CET FYE cutoff data for 2025 (latest round). |
| `data/CAP_Cutoff_Data.csv` | Supplementary CAP round cutoff reference data. |
| `data/final_clean_full.csv` | Final merged and cleaned dataset combining multiple rounds across years. |
| `models/fe_forecast.pkl` | Pre-trained forecast model (pickle) used for predictive mode in the MHT-CET Predictor. |
| `model/fake_job_model.pkl` | Trained Logistic Regression model for fake internship/job classification. |
| `model/tfidf_vectorizer.pkl` | Fitted TF-IDF vectorizer corresponding to the trained model. |

> **Note**: The underlying ML model is trained on the publicly available [Fake Job Postings Dataset](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction) from Kaggle, which contains ~17,000 real and fake job postings labeled by fraud status.

---

## 9. Installation Guide

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (for PDF OCR support — Windows users install to `C:\Program Files\Tesseract-OCR\`)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/KNOWCODE-3.0-THE-DOMinators.git
cd KNOWCODE-3.0-THE-DOMinators
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Environment Variables

Create a `.env` file in the project root or export the variables directly:

```bash
# Required for scam detection (LLM)
export MISTRAL_API_KEY=your_mistral_api_key_here

# Required for company verification (Web Search)
export SERPAPI_KEY=your_serpapi_key_here

# Optional: Flask session secret (defaults to a built-in key)
export FLASK_SECRET_KEY=your_secure_random_secret
```

> **Get API Keys:**
> - Mistral AI: [https://console.mistral.ai/](https://console.mistral.ai/)
> - SERP API: [https://serpapi.com/](https://serpapi.com/)

### Step 5: Train the ML Model (if not pre-trained)

If `model/fake_job_model.pkl` does not exist, train the model:

```bash
python train_model.py
```

Make sure you have the fake job postings CSV dataset available. The training script expects columns: `title`, `company_profile`, `description`, `fraudulent`.

---

## 10. How to Run the Project

```bash
# Ensure virtual environment is active
python app.py
```

The application will start on **`http://127.0.0.1:5000`** by default.

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Open your browser and navigate to `http://localhost:5000`.

### Default Login Credentials

| Username | Password | Role |
|---|---|---|
| `admin` | `password123` | Administrator |
| `user` | `demo123` | Demo User |

> **Security Note**: These are demo credentials. In a production deployment, replace the `USERS` dictionary with a proper database-backed authentication system.

---

## 11. Usage Instructions

### Step 1: Login
Navigate to `/login`, enter credentials, and submit.

### Step 2: Select a Plan
After login, you are redirected to `/pricing`. Choose **Free** or **Pro** to unlock service access.

### Step 3: Choose a Service
The `/services` dashboard presents the full menu via a cyberpunk-styled sidebar:

| Service | Path | Description |
|---|---|---|
| DigiPath AI | `/digipath` | DSE Diploma Admission Predictor |
| MHT-CET Predictor | `/cet` | FYE College Admission Predictor |
| Job Scam Detector | `/job` | Paste text, upload PDF, or submit URL |
| Company Checker | `/company` | Search company reputation |
| College Search | `/database` | Search institution database |
| Analytics | `/analytics` | Fraud detection analytics |
| How It Works | `/docs` | LLM pipeline documentation |
| ML Engine | `/ml-engine` | ML model documentation |

### Using DigiPath AI
1. Enter your diploma percentage.
2. Select a course (e.g., Computer Engineering).
3. Select one or more categories (e.g., OPEN, OBC, SC).
4. Choose a prediction model: AI, Weighted, Safe, or Lucky.
5. Click **Predict** — receive a ranked list of colleges with cutoff percentage, your chance level (Safe / Medium / Risky), and three visualizations.

### Using MHT-CET Predictor
1. Enter your MHT-CET percentage.
2. Select city, branch, and category filters.
3. Choose prediction type: **Current Data** or **Forecast** (ML-predicted).
4. Select forecast mode: Trend, Stability, or Hybrid.
5. Click **Predict** — colleges are returned sorted by city priority and cutoff gap.

### Using SnifTern.ai (Job Scam Detector)
1. Navigate to **Job Scam Detector** (`/job`).
2. Choose input method:
   - **Text**: Paste the full job/internship posting text.
   - **PDF**: Upload an offer letter or JD PDF (max 10 MB).
   - **URL**: Paste the job posting URL.
3. Click **Analyze** — receive verdict, confidence score, red flags, green flags, and a recommendation.

### Using Company Checker
1. Navigate to **Company Checker** (`/company`).
2. Enter the company name.
3. Click **Verify** — receive reputation score, risk level, source links, red/green flags from live web search.

---

## 12. Project Workflow

```
User
 │
 ▼
[Login] ──────► [Plan Selection]
                      │
                      ▼
              [Services Dashboard]
                 /    |    |    \
                /     |    |     \
               ▼      ▼    ▼      ▼
          DigiPath   CET  SnifTern  College
          AI         Pred  .ai      Search
          │           │     │
          │           │     │
     Load CSV     Load CSV  │
     Data         Data      ▼
          │           │  [Input: Text/PDF/URL]
          ▼           ▼       │
    Filter &      Filter &    ▼
    Predict       Predict  Level 1: ML Model
    Cutoffs       Cutoffs  (TF-IDF + LogReg)
          │           │       │
          ▼           ▼       ▼
    Render          Render  Level 2: Mistral LLM
    Charts          Charts  (Contextual Analysis)
                            │
                            ▼
                        Level 3: SERP API
                        (Web Reputation Check)
                            │
                            ▼
                      Final Verdict
                  (LEGITIMATE / FAKE / SUSPICIOUS)
                            │
                            ▼
                   Analytics Dashboard
                   (Aggregate + Visualize)
```

---

## 13. Folder Structure

```
KNOWCODE-3.0-THE-DOMinators/
│
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── # --- SCAM DETECTION MODULES ---
├── enhanced_prediction_utils.py    # Level 1: ML scam predictor
├── llm_verification.py             # Level 2: Mistral LLM verifier
├── serp_api_utils.py               # Level 3: SERP API company verifier
├── analytics_dashboard.py          # Real-time analytics engine
├── preprocessing.py                # Text cleaning utilities
├── pdf_handler.py                  # PDF upload & OCR handler
├── scraping_utils.py               # URL scraping utilities
├── ocr_utils.py                    # OCR image-to-text utilities
├── blockchain_verification.py      # Experimental blockchain audit trail
├── resume_analyzer.py              # Experimental resume analyzer
├── train_model.py                  # ML model training script
│
├── # --- DATA FILES ---
├── final_diploma_cleaned.csv       # DSE Round 2 cutoff data
├── old_data.csv                    # DSE Round 1 historical cutoffs
├── detailed_college_database.csv   # Enriched college institution DB
│
├── data/
│   ├── fe_2024.csv                 # MHT-CET FYE cutoff data (2024)
│   ├── fe_2025.csv                 # MHT-CET FYE cutoff data (2025)
│   ├── CAP_Cutoff_Data.csv         # CAP round reference data
│   ├── final_clean_full.csv        # Merged multi-year dataset
│   ├── college_city_map.json       # City-to-college mapping
│   └── convert_dataset.py          # PDF-to-CSV data conversion script
│
├── model/
│   ├── fake_job_model.pkl          # Trained Logistic Regression model
│   └── tfidf_vectorizer.pkl        # Fitted TF-IDF vectorizer
│
├── models/
│   └── fe_forecast.pkl             # MHT-CET forecast model
│
├── templates/
│   ├── home.html                   # Landing page
│   ├── login.html                  # Authentication page
│   ├── pricing.html                # Plan selection page
│   ├── services.html               # Main dashboard with sidebar
│   ├── digipath.html               # DSE Admission Predictor UI
│   ├── cet_predictor.html          # MHT-CET Predictor UI
│   ├── job.html                    # Scam Job Detector UI
│   ├── company.html                # Company Checker UI
│   ├── college_search.html         # College DB Search UI
│   ├── analytics.html              # Analytics Dashboard UI
│   ├── pathway.html                # DSE vs CET pathway selector
│   ├── email.html                  # Email validator / AI chatbot
│   ├── how_it_works.html           # LLM pipeline docs
│   ├── ml_engine.html              # ML model docs
│   ├── 404.html                    # 404 error page
│   └── 500.html                    # 500 error page
│
├── static/
│   ├── css/
│   │   └── style.css               # Global stylesheet
│   └── js/
│       └── script.js               # Frontend JavaScript
│
├── images/                         # Project images / screenshots
│
└── # --- TEST FILES ---
    ├── test_model.py
    ├── test_enhanced_model.py
    ├── test_integrations.py
    └── test_analytics_access.py
```

---

## 14. Future Improvements

- **Database-backed Authentication**: Replace the hardcoded `USERS` dictionary with a proper SQLite/PostgreSQL-backed user management system with hashed passwords.
- **Real-time Model Retraining**: Auto-retrain the ML model periodically with newly detected fraud patterns and user-reported cases.
- **More Admission Streams**: Extend DigiPath AI to cover TFWS (Tuition Fee Waiver Scheme), NRI, and management quota seats.
- **Mobile App**: Develop a React Native or Flutter frontend for on-the-go scam detection.
- **Browser Extension**: A Chrome/Firefox extension to analyze job postings directly on LinkedIn, Internshala, or Naukri.
- **Notification System**: Alert students via email/SMS when a suspicious company they follow posts a new job.
- **Multi-State Data**: Expand college admission data beyond Maharashtra to other Indian states.
- **Advanced NLP**: Replace TF-IDF with transformer-based embeddings (BERT, RoBERTa) for better semantic scam detection.
- **OAuth Integration**: Add Google/GitHub login options.
- **Containerization**: Dockerize the application for easier deployment.

---

## 15. Contributors

**Team THE DOMinators — india next hackthon Hackathon**

| Name | Role |
|---|---|
| Ibrahim Shaikh | Full Stack Developer & ML Engineer |
| Team Member 2 | Backend & API Integration |
| Team Member 3 | Frontend & UI/UX Design |
| Team Member 4 | Data Engineering & Research |

---

## 16. License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 THE DOMinators

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

**Built with passion at india next hackthon by THE DOMinators**

*"Empowering students. Eliminating fraud."*

</div>
