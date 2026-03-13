import logging
import os
import re
import joblib
import math
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any

# --- INITIALIZATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nexora Security Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLInput(BaseModel):
    url: str

# --- ML ENGINE LOADING ---
MODEL_PATH = "advanced_url_model.pkl"
model = None
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logger.info("Neural Engine synchronized.")
except Exception as e:
    logger.error(f"Engine Load Failure: {e}")

# --- SECURITY UTILITIES ---
def get_shannon_entropy(data: str) -> float:
    """Calculates entropy to detect randomized/encrypted strings."""
    if not data:
        return 0.0
    entropy = 0.0
    for x in range(256):
        p_x = float(data.count(chr(x))) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def extract_url_metrics(url: str) -> Dict[str, Any]:
    """Mathematical decomposition of the URL string."""
    clean_url = url.split('://')[-1].split('?')[0]
    return {
        'url_length': len(url),
        'num_hyphens': url.count('-'),
        'num_dots': url.count('.'),
        'num_digits': sum(c.isdigit() for c in url),
        'num_special_chars': len(re.findall(r'[!@#$%^&*()_+|~=`{}\[\]:";\'<>?,.\/]', url)),
        'has_https': 1 if url.startswith('https') else 0,
        'has_tld': 1 if any(tld in url for tld in ['.com', '.in', '.org', '.net', '.gov', '.edu', '.top', '.xyz', '.biz']) else 0,
        'subdomain_depth': clean_url.count('.') - 1,
        'entropy': get_shannon_entropy(url)
    }

# --- THREAT INTELLIGENCE REPOSITORY ---
PROTECTED_ENTITIES = {
    "FINANCE_INDIA": [
        "paytm", "phonepe", "gpay", "bhim", "onlinesbi", "sbi", "hdfcbank", "icicibank", 
        "axisbank", "kotak", "bobibanking", "canarabank", "pnbindia", "idbi", "unionbank"
    ],
    "FINANCE_GLOBAL": [
        "paypal", "stripe", "binance", "coinbase", "kraken", "kucoin", "trustwallet", 
        "metamask", "blockchain", "revolut", "wise", "pioneer"
    ],
    "SOCIAL_MEDIA": [
        "facebook", "instagram", "whatsapp", "telegram", "snapchat", "twitter", "x.com", 
        "linkedin", "discord", "reddit", "tiktok", "pinterest"
    ],
    "ECOMMERCE": [
        "amazon", "flipkart", "meesho", "myntra", "ebay", "aliexpress", "olx", "zomato", 
        "swiggy", "bigbasket", "jiomart", "nykaa"
    ],
    "TECH_SERVICES": [
        "google", "gmail", "microsoft", "outlook", "office365", "icloud", "appleid", 
        "netflix", "disneyplus", "spotify", "dropbox", "github", "heroku", "vercel"
    ],
    "GOVERNMENT": [
        "uidai", "aadhaar", "irctc", "mparivahan", "digilocker", "npscra", "incometax", 
        "epfindia", "ssc.nic", "upsc.gov", "cowin"
    ]
}

PHISHING_TLDS = [
    '.xyz', '.top', '.win', '.loan', '.club', '.online', '.site', '.biz', '.info', 
    '.icu', '.buzz', '.work', '.tk', '.ml', '.ga', '.cf', '.gq'
]

DANGER_KEYWORDS = [
    'login', 'verify', 'account', 'update', 'kyc', 'secure', 'reward', 'gift', 
    'offer', 'win', 'claim', 'refund', 'support', 'billing', 'bonus'
]

# --- SCANNING ENGINE ---
@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # Validation: Structure Check
    if "." not in url or len(url) < 8:
        return {
            "url": url, "is_scam": True, "prediction_code": "STRUCT_ERR",
            "message": "Invalid string structure rejected.", "details": {}
        }

    m = extract_url_metrics(url)
    
    # LAYER 1: BRAND IMITATOR DETECTION
    # Checks if any of the 100+ entities are in the URL but not as the legitimate host.
    domain_part = url.replace('https://','').replace('http://','').replace('www.','').split('/')[0]
    
    for category, brands in PROTECTED_ENTITIES.items():
        for brand in brands:
            if brand in url:
                # If brand is mentioned but isn't the primary domain (e.g. brand.com)
                # This catches 'brand-login.com' or 'brand.secure-update.tk'
                is_legit = False
                # Common legitimate patterns
                legit_patterns = [f"{brand}.com", f"{brand}.in", f"{brand}.org", f"{brand}.net", f"{brand}.sbi", f"{brand}.co"]
                if any(p in domain_part for p in legit_patterns):
                    if domain_part.endswith(tuple(legit_patterns)):
                        is_legit = True
                
                if not is_legit:
                    # Heuristic confirm: If it mentions brand + phishing TLD or hyphen
                    if m['num_hyphens'] > 0 or any(tld in url for tld in PHISHING_TLDS):
                        return {
                            "url": url, "is_scam": True, "prediction_code": "BRAND_SPOOF",
                            "message": f"Security Alert: Unauthorized {brand.upper()} imitation.",
                            "details": m
                        }

    # LAYER 2: ARCHITECTURAL ANOMALY DETECTION
    # A. IP/Port Based Phishing
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        return {
            "url": url, "is_scam": True, "prediction_code": "IP_HOST",
            "message": "Critical: IP-based hosting signature.", "details": m
        }

    # B. Subdomain Nesting (Tunneling)
    if m['subdomain_depth'] >= 3:
        return {
            "url": url, "is_scam": True, "prediction_code": "TUNNEL_DETECT",
            "message": "Suspicious: Deep subdomain nesting detected.", "details": m
        }

    # C. High Entropy (Algorithmically Generated Domains)
    if m['entropy'] > 4.7:
        return {
            "url": url, "is_scam": True, "prediction_code": "ENTROPY_HIGH",
            "message": "Warning: High randomness detected in string.", "details": m
        }

    # LAYER 3: KEYWORD SYNERGY
    keyword_count = sum(1 for word in DANGER_KEYWORDS if word in url)
    if keyword_count >= 1:
        if any(tld in url for tld in PHISHING_TLDS) or m['num_digits'] > 5:
            return {
                "url": url, "is_scam": True, "prediction_code": "PHISH_SYNC",
                "message": "Threat: Phishing keyword and TLD combination.", "details": m
            }

    # LAYER 4: NEURAL NETWORK INFERENCE
    try:
        if model:
            # Feature alignment for Scikit-Learn
            features = [[
                m['url_length'], m['num_hyphens'], m['num_dots'],
                m['num_digits'], m['num_special_chars'], 
                m['has_https'], m['has_tld']
            ]]
            prediction = model.predict(features)[0]
            
            # Logic: 31 = Benign/Safe
            final_scam_status = False if int(prediction) == 31 else True
            
            # Cross-Validation: If AI says safe but digits/hyphens are abnormal, override.
            if not final_scam_status and (m['num_digits'] > 10 or m['num_hyphens'] > 3):
                final_scam_status = True
                prediction = "NEURAL_OVERRIDE"

            return {
                "url": url,
                "is_scam": final_scam_status,
                "prediction_code": str(prediction),
                "message": "Integrity Verified." if not final_scam_status else "Neural Threat Match Found.",
                "details": m
            }
    except Exception as e:
        logger.error(f"Inference Error: {e}")

    # Fallback default
    return {
        "url": url, "is_scam": False, 
        "message": "No immediate threats identified.", "details": m
    }

@app.post("/chat")
async def nexora_chat(data: dict):
    user_input = data.get("message", "").lower()
    return {"response": "Nexora AI actively monitoring network signatures."}
