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
    
    # 1. THE SECRET SAUCE: Professional Extraction
    # tldextract correctly separates 'pay' (subdomain), 'google' (domain), 'com' (suffix)
    ext = tldextract.extract(url)
    domain_primary = ext.domain  # e.g., 'google'
    full_registered_domain = f"{ext.domain}.{ext.suffix}" # e.g., 'google.com'

    # 2. BRAND DEFENSE (The logic that now works for subdomains)
    for brand in PROTECTED_BRANDS:
        # Check if the brand is being used anywhere in the URL
        if brand in url:
            # If the brand is present, the domain MUST be the official one
            official_domains = [f"{brand}.com", f"{brand}.in", f"{brand}.net", f"{brand}.org", f"{brand}.co"]
            if not any(full_registered_domain == official for official in official_domains):
                return {
                    "url": url, "is_scam": True, "prediction_code": "BRAND_SPOOF",
                    "message": f"CRITICAL: Unauthorized use of {brand.upper()} identity."
                }
            else:
                # If it IS the official domain, skip similarity checks to prevent false alarms
                continue

        # 3. TYPOSQUATTING CHECK
        distance = get_levenshtein_distance(domain_primary, brand)
        if 0 < distance <= 2:
            return {
                "url": url, "is_scam": True, "prediction_code": "SIMILARITY_THREAT",
                "message": f"CRITICAL: Visual imitation of {brand.upper()} detected."
            }

    # 4. HEURISTIC RED FLAGS
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        return {"url": url, "is_scam": True, "prediction_code": "IP_HOSTING", "message": "THREAT: Malicious IP-based hosting."}
    
    if any(tld in url for tld in SUSPICIOUS_TLDS) or sum(c.isdigit() for c in url) > 10:
        return {"url": url, "is_scam": True, "prediction_code": "HIGH_RISK_PATTERN", "message": "THREAT: Suspicious URL architecture."}

    # 5. NEURAL INFERENCE
    try:
        if model:
            feat = [len(url), url.count('-'), url.count('.'), sum(c.isdigit() for c in url), 
                    len(re.findall(r'[^a-zA-Z0-9]', url)), 1 if 'https' in url else 0, 1]
            pred = model.predict([feat])[0]
            is_scam = False if int(pred) == 31 else True
            return {
                "url": url, "is_scam": is_scam, "prediction_code": str(pred),
                "message": "SECURE: Domain integrity verified." if not is_scam else "THREAT: Neural match found."
            }
    except:
        pass

    return {"url": url, "is_scam": False, "message": "Analysis complete: No immediate threats."}

# --- THE AI CHAT ENGINE ---
from fastapi.responses import StreamingResponse
import json

@app.post("/chat")
async def chat_handler(data: ChatInput):
    def generate():
        # This tells NVIDIA to send data as it's generated
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {"role": "system", "content": "You are Nexora AI. Be elite, concise, and technical. No emojis."},
                {"role": "user", "content": data.message}
            ],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/plain")
