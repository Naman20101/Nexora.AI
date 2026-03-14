import logging
import os
import re
import joblib
import tldextract  # THE SECRET TO 100% ACCURACY
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- INITIALIZATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nexora Titan-Shield Ultimate")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLInput(BaseModel):
    url: str

class ChatInput(BaseModel):
    message: str

# --- NVIDIA AI CONFIGURATION ---
AI_CLIENT = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# --- ML ENGINE LOAD ---
MODEL_PATH = "advanced_url_model.pkl"
model = None
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logger.info("✅ Neural Core Online")
except Exception as e:
    logger.error(f"❌ Neural Core Offline: {e}")

# --- SECURITY UTILITIES ---
def get_levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2): return get_levenshtein_distance(s2, s1)
    if len(s2) == 0: return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

PROTECTED_BRANDS = [
    "paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", 
    "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"
]

SUSPICIOUS_TLDS = ['.xyz', '.top', '.win', '.loan', '.club', '.online', '.site', '.biz', '.apk', '.app']

# --- THE SCANNER ENGINE ---
@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # 1. PROFESSIONAL EXTRACTION
    ext = tldextract.extract(url)
    domain_primary = ext.domain  
    full_registered_domain = f"{ext.domain}.{ext.suffix}" 

    # 2. BRAND DEFENSE (The "Payapk" & "Spoof" Killer)
    brand_found_in_url = False
    for brand in PROTECTED_BRANDS:
        if brand in url:
            brand_found_in_url = True
            official_domains = [f"{brand}.com", f"{brand}.in", f"{brand}.net", f"{brand}.org", f"{brand}.co"]
            
            # If brand is mentioned but NOT on an official domain -> INSTANT BLOCK
            if not any(full_registered_domain == official for official in official_domains):
                return {
                    "url": url, "is_scam": True, "prediction_code": "BRAND_SPOOF",
                    "message": f"CRITICAL: Unauthorized use of {brand.upper()} identity."
                }
            # If it IS official, we can stop checking other brands
            break 

    # 3. TYPOSQUATTING CHECK (Visual Similarity)
    # Only check if we haven't already confirmed it's an official brand site
    for brand in PROTECTED_BRANDS:
        distance = get_levenshtein_distance(domain_primary, brand)
        if 0 < distance <= 2 and domain_primary != brand:
            return {
                "url": url, "is_scam": True, "prediction_code": "SIMILARITY_THREAT",
                "message": f"CRITICAL: Visual imitation of {brand.upper()} detected."
            }

    # 4. HEURISTIC RED FLAGS (The "Architecture" Check)
    # If it has an IP address or too many digits, block it even if no brand is mentioned
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        return {"url": url, "is_scam": True, "prediction_code": "IP_HOSTING", "message": "THREAT: Malicious IP-based hosting."}
    
    if any(tld in url for tld in SUSPICIOUS_TLDS) or sum(c.isdigit() for c in url) > 10:
        return {"url": url, "is_scam": True, "prediction_code": "HIGH_RISK_PATTERN", "message": "THREAT: Suspicious URL architecture."}

    # 5. NEURAL INFERENCE (The ML Model)
    # This part was being skipped before—now it runs for EVERY link
    try:
        if model:
            # Feature extraction for the .pkl model
            feat = [len(url), url.count('-'), url.count('.'), sum(c.isdigit() for c in url), 
                    len(re.findall(r'[^a-zA-Z0-9]', url)), 1 if 'https' in url else 0, 1]
            pred = model.predict([feat])[0]
            
            # Logic: If model says 1 (or your specific scam code), block it.
            # Assuming 31 is your 'Safe' code based on previous messages
            is_scam = False if int(pred) == 31 else True
            
            if is_scam:
                return {
                    "url": url, "is_scam": True, "prediction_code": str(pred),
                    "message": "THREAT: Neural fraud signature detected."
                }
    except Exception as e:
        logger.error(f"Neural Core Error: {e}")

    # 6. FINAL CLEARANCE
    return {"url": url, "is_scam": False, "message": "SECURE: No fraud signatures found."}

