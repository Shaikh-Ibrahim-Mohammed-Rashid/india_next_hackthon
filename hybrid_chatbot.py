import os
import json
import pickle
import random
import re
import requests
import numpy as np
import nltk
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity

# ── API Keys ───────────────────────────────────────────────────────────────────
GROQ_KEY   = os.environ.get("GROQ_API_KEY",   "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")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY",  "AIzaSyARZsd1QcSsBitUONcEsf3xYS24TP7F_pM")
AI_PROVIDER = "groq"  # "groq" or "gemini"

nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
nltk.download('punkt_tab', quiet=True)

BASE = os.path.dirname(os.path.abspath(__file__))
app  = Flask(
    __name__,
    template_folder = os.path.join(BASE, "templates"),
    static_folder   = os.path.join(BASE, "static"),
)
CORS(app, supports_credentials=True)
MODEL_DIR = os.path.join(BASE, "chatbot_model")

# ── Load ML model ──────────────────────────────────────────────────────────────
print("📦 Loading chatbot model...")
try:
    vectorizer = pickle.load(open(os.path.join(MODEL_DIR, "vectorizer.pkl"),    "rb"))
    model      = pickle.load(open(os.path.join(MODEL_DIR, "model.pkl"),         "rb"))
    le         = pickle.load(open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "rb"))
    responses  = pickle.load(open(os.path.join(MODEL_DIR, "responses.pkl"),     "rb"))
    domain_map = pickle.load(open(os.path.join(MODEL_DIR, "domain_map.pkl"),    "rb"))
    with open(os.path.join(MODEL_DIR, "meta.json")) as f:
        meta = json.load(f)
    print(f"✅ ML model loaded — {meta['intents']} intents | {meta['accuracy']}% accuracy")
except FileNotFoundError as e:
    print(f"❌ Model not found: {e}\n   Run chatbot_train.py first!")
    exit(1)

# ── Build semantic index ───────────────────────────────────────────────────────
DATASET_PATH = os.path.join(BASE, "college_faq_final.json")
ALL_PATTERNS = []
TAG_VECTORS  = {}

print("📦 Building semantic index...")
try:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    _keep  = {"no","not","how","what","when","where","which","who","why",
               "can","do","is","are","fee","free","safe","hack","risk"}
    _stops = set(stopwords.words('english')) - _keep
    _lemm  = WordNetLemmatizer()

    def _clean(text):
        tokens = nltk.word_tokenize(text.lower())
        return " ".join(_lemm.lemmatize(t) for t in tokens
                        if t.isalpha() and t not in _stops)

    tag_to_patterns = {}
    for intent in dataset["intents"]:
        tag = intent["tag"]
        for p in intent.get("patterns", []):
            ALL_PATTERNS.append((p.lower().strip(), tag))
            tag_to_patterns.setdefault(tag, []).append(_clean(p))

    for tag, cleaned in tag_to_patterns.items():
        vecs = vectorizer.transform(cleaned)
        TAG_VECTORS[tag] = np.asarray(vecs.mean(axis=0))

    print(f"✅ Semantic index — {len(TAG_VECTORS)} tags | {len(ALL_PATTERNS)} patterns")
except Exception as e:
    print(f"⚠️  Semantic index failed: {e}")

# ── NLP helpers ────────────────────────────────────────────────────────────────
KEEP       = {"no","not","how","what","when","where","which","who","why",
              "can","do","is","are","fee","free","safe","hack","risk"}
stop_words = set(stopwords.words('english')) - KEEP
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    tokens = nltk.word_tokenize(text.lower().strip())
    return " ".join(lemmatizer.lemmatize(t) for t in tokens
                    if t.isalpha() and t not in stop_words)

# ── Thresholds ─────────────────────────────────────────────────────────────────
ML_THRESHOLD       = 0.35
SEMANTIC_THRESHOLD = 0.20

# ── System prompt for AI ───────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are DigiPath Assistant — an AI guide for students in Mumbai, Maharashtra.
You help with TWO domains:

1. COLLEGE ADMISSIONS (Mumbai & Maharashtra):
- Colleges: IIT Bombay, VJTI, SPIT, DJSCE, KJSCE, TSEC, VESIT, SAKEC, SPCE, CRCE, COEP Pune, RAIT, MPSTME/NMIMS
- Fees: VJTI ~₹60k/year, DJSCE ~₹74k-2.2L/year, IIT Bombay ~₹2L/year
- Placements: VJTI avg ₹16.35 LPA, DJSCE avg ₹11.1 LPA, IIT Bombay avg ₹23.5 LPA
- Admission: MHT-CET + CAP rounds via dte.maharashtra.gov.in
- Scholarships: EBC freeship, SC/ST — mahadbt.maharashtra.gov.in
- Percentile guide:
  99.5%+ → VJTI CSE, SPIT CSE, DJSCE CSE
  97-99% → TSEC, KJSCE, VESIT
  90-96% → SAKEC, SPCE, CRCE, RAIT
  80-89% → SAKEC, RAIT, Atharva, MGM, KES
  70-79% → Private Mumbai colleges
  Below 70% → Institute-level round

2. CYBERSECURITY:
- Attacks: Phishing, Malware, Ransomware, DDoS, SQL Injection, XSS, MITM, Social Engineering
- Job/Internship Scams: fake HR emails, OTP fraud, advance fee scams, fake offer letters
- Defense: Firewalls, VPN, Encryption, Zero Trust, MFA, Password managers
- Career: CEH, OSCP, CompTIA Security+, CISSP — avg ₹8-25 LPA in India
- Tools: Nmap, Metasploit, Wireshark, Burp Suite, Kali Linux
- Penetration testing: 5 phases — Recon → Scan → Exploit → Post-exploit → Report
- India laws: IT Act 2000, Section 66, cybercrime.gov.in, helpline 1930

RESPONSE RULES:
- Be concise and helpful (max 250 words)
- Use bullet points for lists
- Use ₹ for Indian currency
- Answer in the same language the user writes in (Hindi/Hinglish/English)
- If asked something completely unrelated to colleges or cybersecurity, politely redirect
- Never make up specific numbers you are not sure about"""

# ── SHORTCUTS — Layer 1 keyword matching ──────────────────────────────────────
SHORTCUTS = {
    r'\b(hi|hello|hey|namaste|hii|helo)\b':                         "greeting",
    r'\b(bye|goodbye|see you|cya|alvida)\b':                        "goodbye",
    r'\b(thanks?|thank you|thx|shukriya|dhanyawad)\b':              "thanks",
    # Scam/fraud — placed ABOVE internship to match first
    r'\b(scam|fraud|fake job|job fraud|internship scam|internship fraud|fake offer|fake hr|fake letter)\b': "cyber_social_engineering",
    r'\b(vjti)\b':                                                  "vjti_mumbai",
    r'\b(spit)\b':                                                  "spit_mumbai",
    r'\b(djsce|dj sanghvi)\b':                                     "djsce_mumbai",
    r'\b(kjsce|kj somaiya|somaiya)\b':                             "kjsce_mumbai",
    r'\b(tsec)\b':                                                  "tsec_mumbai",
    r'\b(vesit)\b':                                                 "vesit_mumbai",
    r'\b(sakec)\b':                                                 "sakec_mumbai",
    r'\b(mpstme|nmims)\b':                                          "mpstme_mumbai",
    r'\b(spce)\b':                                                  "spce_mumbai",
    r'\b(crce)\b':                                                  "crce_mumbai",
    r'\b(coep)\b':                                                  "coep_pune",
    r'\b(rait)\b':                                                  "rait_navi_mumbai",
    r'\b(iit bombay|iitb|iit powai)\b':                            "iit_bombay",
    r'\b(mht.?cet|maharashtra cet)\b':                             "mht_cet_info",
    r'\b(cap round)\b':                                             "cap_round",
    r'\b(scholarship|freeship|mahadbt)\b':                          "scholarship",
    r'\b(hostel)\b':                                                "hostel_mumbai",
    r'\b(internship|internships)\b':                                "internship",
    r'\b(lateral entry|dsy)\b':                                     "lateral_entry",
    r'\b(attendance)\b':                                            "attendance",
    r'\b(atkt|backlog|kt exam)\b':                                  "revaluation",
    r'\b(phishing)\b':                                              "cyber_phishing",
    r'\b(malware|virus|trojan|worm)\b':                             "cyber_malware",
    r'\b(ransomware)\b':                                            "cyber_ransomware",
    r'\b(ddos|denial of service)\b':                                "cyber_ddos",
    r'\b(sql injection|sqli)\b':                                    "cyber_sql_injection",
    r'\b(xss|cross.?site scripting)\b':                             "cyber_xss",
    r'\b(vpn)\b':                                                   "cyber_vpn",
    r'\b(firewall)\b':                                              "cyber_firewall",
    r'\b(encryption|cryptography)\b':                               "cyber_encryption",
    r'\b(ethical hack|pen test|pentest|penetration test|penetration testing)\b': "cyber_ethical_hacking",
    r'\b(oscp|ceh|security\+|cissp)\b':                             "cyber_certifications",
    r'\b(social engineering)\b':                                    "cyber_social_engineering",
    r'\b(cyber law|it act|section 66)\b':                           "cyber_india_laws",
    r'\b(zero trust)\b':                                            "cyber_zero_trust",
    r'\b(osint)\b':                                                 "cyber_osint",
    r'\b(ctf|capture the flag)\b':                                  "cyber_ctf",
    r'\b(network security)\b':                                      "cyber_network_security",
    r'\b(cloud security)\b':                                        "cyber_cloud_security",
    r'\b(incident response|soc analyst)\b':                         "cyber_incident_response",
}

# ── ML functions ───────────────────────────────────────────────────────────────
def keyword_match(text):
    t = text.lower()
    for pattern, tag in SHORTCUTS.items():
        if re.search(pattern, t):
            return tag
    return None

def semantic_search(text):
    if not TAG_VECTORS:
        return None, 0.0
    q_vec  = vectorizer.transform([preprocess(text)])
    q_arr  = np.asarray(q_vec.todense())
    scores = [(tag, float(cosine_similarity(q_arr, vec)[0][0]))
              for tag, vec in TAG_VECTORS.items()]
    scores.sort(key=lambda x: -x[1])
    return scores[0]

def ml_classify(text):
    vec = vectorizer.transform([preprocess(text)])
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(vec)[0]
        idx   = int(probs.argmax())
        return le.classes_[idx], float(probs[idx])
    else:
        dec   = model.decision_function(vec)[0]
        idx   = int(dec.argmax())
        exp_s = np.exp(dec - dec.max())
        return le.classes_[idx], float(exp_s[idx] / exp_s.sum())

# ── Groq API ───────────────────────────────────────────────────────────────────
# Groq available models (free): llama-3.3-70b-versatile, llama-3.1-8b-instant,
#                                mixtral-8x7b-32768, gemma2-9b-it
GROQ_MODELS = [
    "llama-3.3-70b-versatile",   # best quality, still free
    "llama-3.1-8b-instant",      # fastest
    "mixtral-8x7b-32768",        # good fallback
]

def call_groq(user_message, local_hint=None):
    if not GROQ_KEY or GROQ_KEY == "YOUR_NEW_GROQ_KEY_HERE":
        print("  ⚠️  Groq key not set")
        return None, "no_key"

    content = user_message
    if local_hint:
        content = (f"Student question: {user_message}\n\n"
                   f"Relevant context from my knowledge base:\n{local_hint}\n\n"
                   f"Using this context and your knowledge, give a complete helpful answer.")

    # Try models in order until one works
    for model_name in GROQ_MODELS:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_KEY}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":    model_name,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": content},
                    ],
                    "max_tokens":  450,
                    "temperature": 0.5,
                },
                timeout=12,
            )

            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"].strip()
                print(f"  ✅ Groq success ({model_name})")
                return text, "groq"

            # 429 = rate limit, try next model
            # 404 = model not found, try next model
            if resp.status_code in [429, 404]:
                print(f"  ⚠️  Groq {resp.status_code} on {model_name}, trying next...")
                continue

            print(f"  ❌ Groq HTTP {resp.status_code}: {resp.text[:150]}")
            return None, f"groq_{resp.status_code}"

        except requests.Timeout:
            print(f"  ⚠️  Groq timeout on {model_name}, trying next...")
            continue
        except Exception as e:
            print(f"  ❌ Groq error: {e}")
            return None, "error"

    return None, "all_models_failed"

# ── Gemini API ─────────────────────────────────────────────────────────────────
def call_gemini(user_message, local_hint=None):
    if not GEMINI_KEY or GEMINI_KEY == "YOUR_GEMINI_KEY_HERE":
        return None, "no_key"

    content = user_message
    if local_hint:
        content = f"Context: {local_hint}\n\nQuestion: {user_message}"

    try:
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\n{content}"}]}],
                "generationConfig": {"maxOutputTokens": 450, "temperature": 0.5}
            },
            timeout=14,
        )
        if resp.status_code == 200:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"  ✅ Gemini success")
            return text, "gemini"
        print(f"  ❌ Gemini HTTP {resp.status_code}: {resp.text[:120]}")
        return None, f"gemini_{resp.status_code}"
    except requests.Timeout:
        return None, "timeout"
    except Exception as e:
        print(f"  ❌ Gemini error: {e}")
        return None, "error"

# ── Unified AI call — tries both providers ─────────────────────────────────────
def call_ai(user_message, local_hint=None):
    if AI_PROVIDER == "gemini":
        result, status = call_gemini(user_message, local_hint)
        if result: return result, "gemini"
        result, status = call_groq(user_message, local_hint)
        if result: return result, "groq"
    else:
        result, status = call_groq(user_message, local_hint)
        if result: return result, "groq"
        result, status = call_gemini(user_message, local_hint)
        if result: return result, "gemini"
    return None, status

# ── Smart fallback ─────────────────────────────────────────────────────────────
def smart_fallback(text):
    msg = text.lower()
    if any(w in msg for w in ["college","fees","admission","cutoff","placement",
                               "hostel","scholarship","percentile","engineering"]):
        return ("For Maharashtra engineering admissions:\n"
                "• DTE Maharashtra: dte.maharashtra.gov.in\n"
                "• NIRF Rankings: nirfindia.org\n\n"
                "Tell me your MHT-CET percentile and preferred branch — "
                "I'll suggest the best colleges for you!")
    if any(w in msg for w in ["cyber","hack","security","attack","phish",
                               "malware","scam","fraud","pentest","virus"]):
        return ("I'm your cybersecurity guide! Try asking:\n"
                "• 'What is phishing?'\n"
                "• 'How does ransomware work?'\n"
                "• 'How do internship scams work?'\n"
                "• 'Ethical hacking career and salary'")
    return ("I can help with:\n"
            "🎓 College admissions, fees, placements in Mumbai\n"
            "🔐 Cybersecurity concepts, careers, certifications\n\n"
            "Try: 'Tell me about VJTI' or 'What is SQL injection?'")

# ── CORS ───────────────────────────────────────────────────────────────────────
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return render_template("chatbot.html")

@app.route("/api", methods=["GET"])
def health():
    groq_ok   = bool(GROQ_KEY)   and GROQ_KEY   != "YOUR_NEW_GROQ_KEY_HERE"
    gemini_ok = bool(GEMINI_KEY) and GEMINI_KEY != "YOUR_GEMINI_KEY_HERE"
    return jsonify({
        "status":    "DigiPath Hybrid Chatbot v5.0 ✅",
        "intents":   meta["intents"],
        "patterns":  meta["patterns"],
        "accuracy":  meta["accuracy"],
        "model":     meta.get("model", ""),
        "mode":      "Keyword → Semantic → ML → Free AI",
        "groq":      "✅ ready" if groq_ok   else "❌ key needed",
        "gemini":    "✅ ready" if gemini_ok else "❌ key needed",
        "provider":  AI_PROVIDER,
        "domains":   meta.get("domains", {}),
    })

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data    = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    print(f"\n── Query: {message[:70]}")

    # ── L1: Keyword ───────────────────────────────────────────────────────
    kw_tag = keyword_match(message)
    if kw_tag and kw_tag in responses:
        resp   = random.choice(responses[kw_tag])
        domain = domain_map.get(kw_tag, "general")
        print(f"   ✅ L1 KEYWORD → {kw_tag}")
        return jsonify({
            "intent": kw_tag, "domain": domain,
            "confidence": 95.0, "response": resp,
            "source": "keyword_match", "is_fallback": False,
        })

    # ── L2+L3: Semantic + ML ──────────────────────────────────────────────
    sem_tag, sem_score = semantic_search(message)
    ml_tag,  ml_conf   = ml_classify(message)
    print(f"   L2 SEMANTIC → {sem_tag} ({sem_score:.3f})")
    print(f"   L3 ML       → {ml_tag}  ({ml_conf:.3f})")

    if sem_tag == ml_tag and sem_score >= SEMANTIC_THRESHOLD:
        resp   = random.choice(responses.get(sem_tag, [""]))
        domain = domain_map.get(sem_tag, "general")
        conf   = min(95.0, (sem_score * 60 + ml_conf * 40) * 100)
        print(f"   ✅ HYBRID → {sem_tag}")
        return jsonify({
            "intent": sem_tag, "domain": domain,
            "confidence": round(conf, 1), "response": resp,
            "source": "hybrid_agreement", "is_fallback": False,
        })

    if sem_score >= SEMANTIC_THRESHOLD and sem_tag in responses:
        resp   = random.choice(responses[sem_tag])
        domain = domain_map.get(sem_tag, "general")
        print(f"   ✅ SEMANTIC → {sem_tag}")
        return jsonify({
            "intent": sem_tag, "domain": domain,
            "confidence": round(sem_score * 100, 1), "response": resp,
            "source": "semantic_wins", "is_fallback": False,
        })

    if ml_conf >= ML_THRESHOLD and ml_tag in responses:
        resp   = random.choice(responses[ml_tag])
        domain = domain_map.get(ml_tag, "general")
        print(f"   ✅ ML → {ml_tag}")
        return jsonify({
            "intent": ml_tag, "domain": domain,
            "confidence": round(ml_conf * 100, 1), "response": resp,
            "source": "ml_wins", "is_fallback": False,
        })

    # ── L4: AI API ────────────────────────────────────────────────────────
    best_tag   = sem_tag if sem_score >= ml_conf else ml_tag
    best_score = max(sem_score, ml_conf)

    local_hint = None
    if best_score >= 0.08 and best_tag in responses:
        local_hint = random.choice(responses[best_tag])

    print(f"   → L4 AI ({AI_PROVIDER}) [{best_tag} @ {best_score:.3f}]")
    ai_resp, status = call_ai(message, local_hint=local_hint)

    if ai_resp:
        domain = domain_map.get(best_tag, "general")
        print(f"   ✅ AI SUCCESS ({status})")
        return jsonify({
            "intent":      best_tag,
            "domain":      domain,
            "confidence":  round(best_score * 100, 1),
            "response":    ai_resp,
            "source":      status,
            "is_fallback": False,
        })

    # ── L5: Fallback ──────────────────────────────────────────────────────
    print(f"   ⚠️  FALLBACK ({status})")
    return jsonify({
        "intent":      "fallback",
        "domain":      "general",
        "confidence":  round(best_score * 100, 1),
        "response":    smart_fallback(message),
        "source":      "fallback",
        "is_fallback": True,
    })

@app.route("/suggest", methods=["GET"])
def suggest():
    return jsonify({"suggestions": [
        "Tell me about VJTI", "DJSCE fees and placement",
        "MHT-CET cutoff for top colleges", "Best college for CS in Mumbai",
        "For 80% which college is best?", "What scholarships are available?",
        "What is phishing attack?", "How does ransomware work?",
        "How do internship scams work?", "Cybersecurity career options",
        "IIT Bombay placement package", "Penetration testing guide",
    ]})

if __name__ == "__main__":
    groq_ok   = bool(GROQ_KEY)   and GROQ_KEY   != "YOUR_NEW_GROQ_KEY_HERE"
    gemini_ok = bool(GEMINI_KEY) and GEMINI_KEY != "YOUR_GEMINI_KEY_HERE"
    print(f"\n{'='*55}")
    print(f"  🚀 DigiPath Hybrid Chatbot v5.0")
    print(f"  Model    : {meta['model']} ({meta['accuracy']}%)")
    print(f"  Intents  : {meta['intents']} | Patterns: {meta['patterns']}")
    print(f"  Layers   : Keyword → Semantic → ML → Free AI")
    print(f"  Groq     : {'✅ Ready' if groq_ok   else '❌ Add key — console.groq.com'}")
    print(f"  Gemini   : {'✅ Ready' if gemini_ok else '❌ Add key — aistudio.google.com'}")
    print(f"  Provider : {AI_PROVIDER}")
    print(f"  UI       : http://localhost:5001/")
    print(f"{'='*55}\n")
    app.run(debug=False, port=5001, host="0.0.0.0")