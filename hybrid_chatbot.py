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

# ── API Key ────────────────────────────────────────────────────────────────────
CLAUDE_KEY = os.environ.get("ANTHROPIC_API_KEY", "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")

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

# ── Config ─────────────────────────────────────────────────────────────────────
ML_THRESHOLD       = 0.55
SEMANTIC_THRESHOLD = 0.28
CLAUDE_API_URL     = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL       = "claude-sonnet-4-20250514"

DATASET_CONTEXT = """You are DigiPath College & Cybersecurity Assistant for students in Mumbai, Maharashtra.

COLLEGE KNOWLEDGE:
- Top colleges: IIT Bombay, VJTI, SPIT, DJSCE, KJSCE, TSEC, VESIT, SAKEC, SPCE, CRCE, COEP Pune, RAIT, MPSTME (NMIMS)
- Key facts: VJTI fees ~₹60k/year (best ROI), DJSCE avg ₹11.1 LPA, IIT Bombay avg ₹23.5 LPA, KJSCE highest ₹58 LPA
- Admission: MHT-CET + CAP rounds via DTE Maharashtra (dte.maharashtra.gov.in)
- Scholarships: EBC freeship, SC/ST govt scholarship — apply at mahadbt.maharashtra.gov.in

PERCENTILE → COLLEGE GUIDE:
- 99.5%+ → VJTI, SPIT, DJSCE (top tier)
- 97–99% → TSEC, KJSCE, VESIT
- 90–96% → SAKEC, SPCE, CRCE, RAIT
- 80–89% → SAKEC, RAIT, Atharva, MGM, KES
- 70–79% → Private colleges in Mumbai suburbs
- Below 70% → Institute-level round colleges

CYBERSECURITY KNOWLEDGE:
- Attacks: Phishing, Malware, Ransomware, DDoS, SQL Injection, XSS, MITM, Social Engineering
- Defense: Firewalls, VPN, Encryption, Zero Trust, MFA, Password Security
- Career: CEH, OSCP, CompTIA Security+, CISSP — avg ₹8–25 LPA in India
- Tools: Nmap, Metasploit, Wireshark, Burp Suite, Kali Linux
- Penetration Testing: Legal ethical hacking, 5 phases: Recon→Scan→Exploit→Maintain→Report
- India laws: IT Act 2000, Section 66, cybercrime.gov.in, helpline 1930

RESPONSE RULES:
- Be concise (max 200 words), use bullet points for lists
- Use ₹ for Indian currency
- For unknown colleges: give general guidance + mention DTE Maharashtra
- Stay in college/cybersecurity context only
- Never fabricate specific numbers you are not sure about"""

# ── SHORTCUTS dict (Layer 1 keyword matching) ──────────────────────────────────
SHORTCUTS = {
    r'\b(hi|hello|hey|namaste|hii)\b':                              "greeting",
    r'\b(bye|goodbye|see you|cya)\b':                               "goodbye",
    r'\b(thanks?|thank you|thx)\b':                                 "thanks",
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
    r'\b(internship)\b':                                            "internship",
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

# ── Core functions ─────────────────────────────────────────────────────────────

def keyword_match(text):
    t = text.lower()
    for pattern, tag in SHORTCUTS.items():
        if re.search(pattern, t):
            return tag
    return None


def semantic_search(text):
    if not TAG_VECTORS:
        return None, 0.0
    q_vec = vectorizer.transform([preprocess(text)])
    q_arr = np.asarray(q_vec.todense())
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


def claude_api(user_message, local_hint=None):
    if local_hint:
        content = (
            f"Student question: {user_message}\n\n"
            f"Context from my dataset (may be partial):\n{local_hint}\n\n"
            f"Give a complete, helpful, concise answer."
        )
    else:
        content = user_message

    headers = {
        "Content-Type":      "application/json",
        "anthropic-version": "2023-06-01",
    }
    if CLAUDE_KEY:
        headers["x-api-key"] = CLAUDE_KEY

    try:
        resp = requests.post(
            CLAUDE_API_URL,
            json={
                "model":      CLAUDE_MODEL,
                "max_tokens": 500,
                "system":     DATASET_CONTEXT,
                "messages":   [{"role": "user", "content": content}],
            },
            headers = headers,
            timeout = 15,
        )
        if resp.status_code == 200:
            return resp.json()["content"][0]["text"].strip(), "claude"
        print(f"  ❌ Claude HTTP {resp.status_code}: {resp.text[:150]}")
        return None, f"http_{resp.status_code}"
    except requests.Timeout:
        print("  ❌ Claude timeout")
        return None, "timeout"
    except Exception as e:
        print(f"  ❌ Claude error: {e}")
        return None, "error"


def smart_fallback(text):
    msg = text.lower()
    if any(w in msg for w in ["college","fees","admission","cutoff","placement",
                               "hostel","scholarship","percentile"]):
        return ("For Maharashtra engineering admissions:\n"
                "• Visit dte.maharashtra.gov.in\n"
                "• Check NIRF: nirfindia.org\n\n"
                "Tell me your percentile + branch for specific college suggestions!")
    if any(w in msg for w in ["cyber","hack","security","attack","phish",
                               "malware","pentest","penetration"]):
        return ("I'm your cybersecurity guide! Try:\n"
                "• 'What is phishing?'\n"
                "• 'How does ransomware work?'\n"
                "• 'Ethical hacking career guide'")
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
    return jsonify({
        "status":    "DigiPath Hybrid Chatbot v4.1 ✅",
        "intents":   meta["intents"],
        "patterns":  meta["patterns"],
        "accuracy":  meta["accuracy"],
        "model":     meta.get("model", ""),
        "mode":      "Keyword → Semantic → ML → Claude",
        "claude_key": "set" if CLAUDE_KEY else "not set",
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

    # ── LAYER 1: Keyword match ─────────────────────────────────────────────
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

    # ── LAYER 2 + 3: Semantic + ML ────────────────────────────────────────
    sem_tag, sem_score = semantic_search(message)
    ml_tag,  ml_conf   = ml_classify(message)
    print(f"   L2 SEMANTIC → {sem_tag} ({sem_score:.3f})")
    print(f"   L3 ML       → {ml_tag}  ({ml_conf:.3f})")

    # Both agree
    if sem_tag == ml_tag and sem_score >= SEMANTIC_THRESHOLD:
        resp   = random.choice(responses.get(sem_tag, [""]))
        domain = domain_map.get(sem_tag, "general")
        conf   = min(95.0, (sem_score * 60 + ml_conf * 40) * 100)
        print(f"   ✅ HYBRID AGREEMENT → {sem_tag}")
        return jsonify({
            "intent": sem_tag, "domain": domain,
            "confidence": round(conf, 1), "response": resp,
            "source": "hybrid_agreement", "is_fallback": False,
        })

    # Semantic wins
    if sem_score >= SEMANTIC_THRESHOLD and sem_tag in responses:
        resp   = random.choice(responses[sem_tag])
        domain = domain_map.get(sem_tag, "general")
        print(f"   ✅ SEMANTIC WINS → {sem_tag}")
        return jsonify({
            "intent": sem_tag, "domain": domain,
            "confidence": round(sem_score * 100, 1), "response": resp,
            "source": "semantic_wins", "is_fallback": False,
        })

    # ML wins
    if ml_conf >= ML_THRESHOLD and ml_tag in responses:
        resp   = random.choice(responses[ml_tag])
        domain = domain_map.get(ml_tag, "general")
        print(f"   ✅ ML WINS → {ml_tag}")
        return jsonify({
            "intent": ml_tag, "domain": domain,
            "confidence": round(ml_conf * 100, 1), "response": resp,
            "source": "ml_wins", "is_fallback": False,
        })

    # ── LAYER 4: Claude API ────────────────────────────────────────────────
    best_tag   = sem_tag if sem_score >= ml_conf else ml_tag
    best_score = max(sem_score, ml_conf)

    local_hint = None
    if best_score >= 0.08 and best_tag in responses:
        local_hint = random.choice(responses[best_tag])

    print(f"   → L4 CLAUDE (best local: {best_tag} @ {best_score:.3f})")
    claude_resp, status = claude_api(message, local_hint=local_hint)

    if claude_resp:
        domain = domain_map.get(best_tag, "general")
        print(f"   ✅ CLAUDE SUCCESS")
        return jsonify({
            "intent":      best_tag,
            "domain":      domain,
            "confidence":  round(best_score * 100, 1),
            "response":    claude_resp,
            "source":      "claude",
            "is_fallback": False,
        })

    # ── LAYER 5: Smart fallback ────────────────────────────────────────────
    print(f"   ⚠️  FALLBACK (Claude: {status})")
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
        "Tell me about VJTI",
        "DJSCE fees and placement",
        "MHT-CET cutoff for top colleges",
        "Best college for CS in Mumbai",
        "For 80% which college is best?",
        "What scholarships are available?",
        "What is phishing attack?",
        "How does ransomware work?",
        "Penetration testing guide",
        "Cybersecurity career options",
        "IIT Bombay placement package",
        "Which colleges have hostel in Mumbai?",
    ]})


if __name__ == "__main__":
    key_status = f"✅ Set ({CLAUDE_KEY[:12]}...)" if CLAUDE_KEY else "⚠️  Not set"
    print(f"\n{'='*55}")
    print(f"  🚀 DigiPath Hybrid Chatbot v4.1")
    print(f"  Model    : {meta['model']} ({meta['accuracy']}%)")
    print(f"  Intents  : {meta['intents']} | Patterns: {meta['patterns']}")
    print(f"  Layers   : Keyword → Semantic → ML → Claude")
    print(f"  API Key  : {key_status}")
    print(f"  UI       : http://localhost:5001/")
    print(f"  Health   : http://localhost:5001/api")
    print(f"{'='*55}\n")
    app.run(debug=True, port=5001, host="0.0.0.0")