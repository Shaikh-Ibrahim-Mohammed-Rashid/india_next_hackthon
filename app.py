import whois
import tldextract
from datetime import datetime
import urllib.parse

def check_scam_url(url):
    score = 100
    red_flags = []
    
    # 1. Normalize URL
    if not url.startswith('http'):
        url = 'http://' + url
        
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    
    # 2. Check for Cheap/Suspicious TLDs
    suspicious_tlds = ['xyz', 'top', 'online', 'vip', 'click', 'site']
    if extracted.suffix in suspicious_tlds:
        score -= 30
        red_flags.append(f"Suspicious Top-Level Domain (.{extracted.suffix})")

    # 3. Keyword Heuristics (Look for scammy words in URL)
    scam_keywords = ['guaranteed', 'free-job', 'offer-letter', 'urgent-hiring', 'registration-fee', 'refund']
    for word in scam_keywords:
        if word in url.lower():
            score -= 20
            red_flags.append(f"Suspicious keyword found in URL: '{word}'")
            
    # 4. Domain Age Check (The Ultimate Lie Detector)
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        
        # Handle cases where creation_date is a list
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if creation_date:
            age_days = (datetime.now() - creation_date).days
            if age_days < 30:
                score -= 40
                red_flags.append(f"Domain is very new! Only {age_days} days old. Major Red Flag for jobs.")
            elif age_days < 180:
                score -= 15
                red_flags.append("Domain is relatively new (less than 6 months old). Proceed with caution.")
    except Exception as e:
        score -= 20
        red_flags.append("Could not verify WHOIS data. Domain might be hidden or invalid.")

    # Final Verdict
    if score >= 80:
        status = "Safe ✅"
    elif score >= 50:
        status = "Suspicious ⚠️"
    else:
        status = "Highly Likely a Scam 🚨"
        
    return {"status": status, "score": score, "red_flags": red_flags}

# --- Testing the function ---
# print(check_scam_url("http://tcs-guaranteed-job.xyz"))