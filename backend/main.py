import logging
import os
import re
import joblib
import math
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

# --- NVIDIA AI BRAIN CONFIGURATION ---
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

# --- ADVANCED SECURITY UTILITIES ---
def get_levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates the visual similarity between two words."""
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

# --- THE HARD-CODED "TITAN" RULES ---
PROTECTED_BRANDS = [
    "paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", 
    "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"
]

SUSPICIOUS_TLDS = ['.xyz', '.top', '.win', '.loan', '.club', '.online', '.site', '.biz', '.apk', '.app']

# --- THE SCANNER ENGINE ---
@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # 1. CLEANING THE DOMAIN
    clean_domain = url.replace('https://','').replace('http://','').replace('www.','').split('/')[0]
    domain_primary = clean_domain.split('.')[0]

    # 2. THE BRAND DEFENSE (The "Payapk" Killer)
    for brand in PROTECTED_BRANDS:
        if brand in url:
            official_domains = [f"{brand}.com", f"{brand}.in", f"{brand}.net", f"{brand}.org", f"{brand}.co"]
            if not any(official in clean_domain for official in official_domains):
                return {
                    "url": url, "is_scam": True, "prediction_code": "BRAND_SPOOF",
                    "message": f"CRITICAL: Unauthorized use of {brand.upper()} identity."
                }
        
        distance = get_levenshtein_distance(domain_primary, brand)
        if 0 < distance <= 2:
            return {
                "url": url, "is_scam": True, "prediction_code": "SIMILARITY_THREAT",
                "message": f"CRITICAL: Visual imitation of {brand.upper()} detected."
            }

    # 3. HEURISTIC RED FLAGS
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}', url):
        return {"url": url, "is_scam": True, "prediction_code": "IP_HOSTING", "message": "THREAT: Malicious IP-based hosting."}
    
    if any(tld in url for tld in SUSPICIOUS_TLDS) or sum(c.isdigit() for c in url) > 7:
        return {"url": url, "is_scam": True, "prediction_code": "HIGH_RISK_PATTERN", "message": "THREAT: Suspicious URL architecture."}

    # 4. NEURAL INFERENCE
    try:
        if model:
            feat = [len(url), url.count('-'), url.count('.'), sum(c.isdigit() for c in url), 
                    len(re.findall(r'[^a-zA-Z0-9]', url)), 1 if 'https' in url else 0, 1]
            pred = model.predict([feat])[0]
            
            is_scam = False if int(pred) == 31 else True
            if not is_scam and (url.count('-') > 2 or url.count('.') > 3):
                is_scam = True
                pred = "OVERRIDE"

            return {
                "url": url, "is_scam": is_scam, "prediction_code": str(pred),
                "message": "SECURE: Domain integrity verified." if not is_scam else "THREAT: Neural match found."
            }
    except:
        pass

    return {"url": url, "is_scam": False, "message": "Analysis complete: No immediate threats."}

# --- THE REAL AI ASSISTANT (NVIDIA NIM POWERED) ---
@app.post("/chat")
async def chat_handler(data: ChatInput):
    try:
        completion = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {
                    "role": "system", 
                    "content": "You are Nexora AI, a cold, elite cyber-security entity created by Naman Reddy. You help users identify fraud and secure their digital assets. Keep answers concise and technical. No emojis."
                },
                {"role": "user", "content": data.message}
            ],
            max_tokens=200
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        logger.error(f"AI Brain Error: {e}")
        return {"response": "Neural link unstable. Directing to local backup: How can I help?"}

# --- RENDER DEPLOYMENT ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
