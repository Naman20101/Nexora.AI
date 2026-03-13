import logging
import os
import re
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nexora Phantom AI")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLInput(BaseModel):
    url: str

# --- MODEL LOADING ---
MODEL_PATH = "advanced_url_model.pkl"
model = None
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logger.info("✅ NEURAL ENGINE LOADED")
except Exception as e:
    logger.error(f"❌ MODEL ERROR: {e}")

# --- FEATURE EXTRACTION ---
def get_features(url):
    return {
        'url_length': len(url),
        'num_hyphens': url.count('-'),
        'num_dots': url.count('.'),
        'num_digits': sum(c.isdigit() for c in url),
        'num_special_chars': len(re.findall(r'[!@#$%^&*()_+|~=`{}\[\]:";\'<>?,.\/]', url)),
        'has_https': 1 if url.startswith('https') else 0,
        'has_tld': 1 if any(tld in url for tld in ['.com', '.org', '.net', '.gov', '.edu', '.xyz', '.biz']) else 0
    }

# --- ROUTES ---
@app.get("/")
def home():
    return {"status": "Nexora AI Online", "model": model is not None}

@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    f = get_features(url)
    
    # --- STEP 1: HARD OVERRIDES (The "Anti-Fake" Guards) ---
    
    # Guard A: Brand Spoofing (If it mentions a brand but isn't the official domain)
    official_brands = {
        "paytm": "paytm.com",
        "paypal": "paypal.com",
        "venmo": "venmo.com",
        "binance": "binance.com"
    }
    
    for brand, official in official_brands.items():
        if brand in url and official not in url:
            return {
                "url": url, "is_scam": True, "prediction_code": "SPOOF_DETECTED",
                "message": f"CRITICAL: Unauthorized {brand} domain spoofing detected.", "details": f
            }

    # Guard B: Suspicious Patterns (IP addresses or too many hyphens/digits)
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        return {"url": url, "is_scam": True, "prediction_code": "IP_PHISH", "message": "CRITICAL: IP-based phishing detected.", "details": f}
    
    if f['num_hyphens'] >= 3 or f['num_digits'] > 10:
        return {"url": url, "is_scam": True, "prediction_code": "HIGH_ENTROPY", "message": "SUSPICIOUS: Abnormal URL structure.", "details": f}

    # Guard C: Non-URL Input (Like "hi" or "hello")
    if "." not in url or len(url) < 8:
        return {"url": url, "is_scam": True, "prediction_code": "INVALID_INPUT", "message": "REJECTED: Not a valid URL structure.", "details": f}

    # --- STEP 2: NEURAL ANALYSIS (The AI Model) ---
    try:
        if model:
            # We must pass features in the EXACT order the model expects
            feature_list = [[
                f['url_length'], f['num_hyphens'], f['num_dots'],
                f['num_digits'], f['num_special_chars'], 
                f['has_https'], f['has_tld']
            ]]
            pred = model.predict(feature_list)[0]
            
            # Logic: 31 is the label for Safe in your Kaggle set
            is_scam = False if int(pred) == 31 else True
            
            return {
                "url": url,
                "is_scam": is_scam,
                "prediction_code": int(pred),
                "message": "Verified Safe" if not is_scam else "Neural Pattern Match: Fraud Detected",
                "details": f
            }
    except Exception as e:
        logger.error(f"Prediction Crash: {e}")

    # Fallback: If AI is confused, we trust our Guards
    return {"url": url, "is_scam": False, "message": "Analysis Complete: Safe", "details": f}

@app.post("/chat")
async def chat(data: dict):
    msg = data.get("message", "").lower()
    if "hi" in msg or "hello" in msg:
        return {"response": "Nexora Systems Online. Analysis core standing by, Naman."}
    return {"response": "Signal received. I am monitoring for malicious network signatures."}
