import logging
import os
import re
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nexora.ai Stealth Intelligence")

# --- CORS CONFIGURATION ---
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
        logger.info("✅ NEURAL ENGINE: Online and Loaded.")
    else:
        logger.error(f"❌ NEURAL ENGINE: {MODEL_PATH} not found.")
except Exception as e:
    logger.error(f"❌ NEURAL ENGINE: Loading failed: {e}")

# --- FEATURE EXTRACTION ---
def get_features_from_url(url):
    """
    Extracts numerical features from the URL for the ML model.
    """
    url_clean = url.replace('https://', '').replace('http://', '').replace('www.', '')
    
    features = {
        'url_length': len(url),
        'num_hyphens': url.count('-'),
        'num_dots': url.count('.'),
        'num_digits': sum(c.isdigit() for c in url),
        'num_special_chars': len(re.findall(r'[!@#$%^&*()_+|~=`{}\[\]:";\'<>?,.\/]', url)),
        'has_https': 1 if url.startswith('https') else 0,
        'num_subdomains': url.count('.') - 1 if url.count('.') > 1 else 0
    }
    tlds = ['.com', '.org', '.net', '.gov', '.edu']
    features['has_tld'] = 1 if any(tld in url for tld in tlds) else 0
    return features

# --- ROUTES ---
@app.get("/")
def health_check():
    return {
        "status": "online",
        "system": "Nexora Phantom V2",
        "model_active": model is not None
    }

@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    f = get_features_from_url(url)
    
    # 1. HEURISTIC OVERRIDE: Catch obvious phishing before the AI
    # Rule A: IP Addresses are almost always malicious in this context
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        return {
            "url": url,
            "is_scam": True,
            "prediction_code": "FLAG_IP_ADDR",
            "message": "CRITICAL: IP-based domain detected.",
            "details": f
        }

    # Rule B: Excessive hyphens or digits (Classic scam pattern)
    if f['num_hyphens'] >= 4 or f['num_digits'] > 12:
        return {
            "url": url,
            "is_scam": True,
            "prediction_code": "FLAG_HIGH_ENTROPY",
            "message": "SUSPICIOUS: Abnormal character density.",
            "details": f
        }

    # Rule C: Input validation
    if len(url) < 8 or "." not in url:
        return {
            "url": url,
            "is_scam": True,
            "prediction_code": "FLAG_INVALID",
            "message": "ERROR: Invalid URL structure.",
            "details": f
        }

    # 2. NEURAL ANALYSIS: Ask the AI Model
    try:
        if model:
            # Match the feature order used during training
            feature_list = [[
                f['url_length'], f['num_hyphens'], f['num_dots'],
                f['num_digits'], f['num_special_chars'], 
                f['has_https'], f['has_tld']
            ]]
            
            pred = model.predict(feature_list)[0]
            
            # Logic: 31 is the Kaggle label for "Benign" (Safe)
            is_scam = False if int(pred) == 31 else True
            
            return {
                "url": url,
                "is_scam": is_scam,
                "prediction_code": int(pred),
                "message": "Verified Official Domain" if not is_scam else "Neural Match: Known Fraud Pattern",
                "details": f
            }
        else:
            # Fallback if model failed to load
            return {
                "url": url,
                "is_scam": False,
                "prediction_code": "OFFLINE",
                "message": "Engine Offline: Basic check passed.",
                "details": f
            }

    except Exception as e:
        logger.error(f"Scan Error: {e}")
        raise HTTPException(status_code=500, detail="Internal analysis failure")

@app.post("/chat")
async def nexora_chat(data: dict):
    msg = data.get("message", "").lower()
    
    if any(x in msg for x in ["hi", "hello", "hey"]):
        resp = "Systems active. I am Nexora AI. Send me a link for neural analysis, Naman."
    elif "status" in msg:
        resp = f"Neural Engine: {'ONLINE' if model else 'OFFLINE'}. Core temperature nominal."
    elif "who made you" in msg:
        resp = "I am a proprietary intelligence developed by Naman Reddy for payment security."
    elif "scam" in msg or "fraud" in msg:
        resp = "I scan URLs for 'fingerprints' like subdomain nesting and entropy levels that signal a phishing attempt."
    else:
        resp = "Command received. My primary directive is link interrogation. Do you have a URL to audit?"
        
    return {"response": resp}
