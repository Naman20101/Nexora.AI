import logging
import os
import re
import joblib
import tldextract 
import openai
import socket  # Added for real-world web verification
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

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

def domain_exists(hostname: str) -> bool:
    """The Ultimate Test: Does this domain actually exist on the web?"""
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        return False

PROTECTED_BRANDS = ["paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"]
TRUSTED_TLDS = ['com', 'in', 'net', 'org', 'co', 'gov', 'edu', 'io', 'me', 'info']

# --- THE SCANNER ENGINE ---
@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # 1. HARD STRUCTURE GATEKEEPER
    # Kills "Nahbri", "Imsafw", and everything without a dot extension
    if "." not in url or len(url.split(".")[-1]) < 2:
        return {
            "url": url, "is_scam": True, "prediction_code": "INVALID_STRUCTURE",
            "message": "THREAT: Input is not a valid URL. Registered domain required."
        }
    
    # 2. EXTRACTION
    ext = tldextract.extract(url)
    domain_primary = ext.domain  
    suffix = ext.suffix
    full_domain = f"{ext.domain}.{ext.suffix}"

    # 3. WEB VERIFICATION (DNS CHECK)
    # If the domain doesn't exist on the actual internet, it's a threat.
    if not domain_exists(full_domain):
        return {
            "url": url, "is_scam": True, "prediction_code": "NON_EXISTENT_DOMAIN",
            "message": "THREAT: Domain not found on the web. Likely fraudulent or gibberish."
        }

    # 4. GIBBERISH & REPETITION FILTER (The "Faaaah" Killer)
    if re.search(r'(.)\1\1', domain_primary):
        return {"url": url, "is_scam": True, "prediction_code": "GIBBERISH_PATTERN", "message": "THREAT: Automated repetitive domain detected."}

    # 5. BRAND DEFENSE
    for brand in PROTECTED_BRANDS:
        if brand in url:
            if full_domain not in [f"{brand}.{tld}" for tld in TRUSTED_TLDS]:
                return {"url": url, "is_scam": True, "prediction_code": "BRAND_HIJACK", "message": f"CRITICAL: Unauthorized use of {brand.upper()} identity."}
            return {"url": url, "is_scam": False, "message": "SECURE: Official brand domain verified."}

    # 6. NEURAL INFERENCE
    if model:
        try:
            feat = [len(url), url.count('-'), url.count('.'), sum(c.isdigit() for c in url), len(re.findall(r'[^a-zA-Z0-9]', url)), 1 if 'https' in url else 0, 1]
            pred = model.predict([feat])[0]
            if int(pred) != 31:
                 return {"url": url, "is_scam": True, "prediction_code": str(pred), "message": "THREAT: Fraudulent signature detected by AI."}
        except: pass

    # 7. FINAL TRUST CHECK
    if suffix not in TRUSTED_TLDS or len(domain_primary) < 4:
         return {"url": url, "is_scam": True, "prediction_code": "LOW_TRUST_SOURCE", "message": "THREAT: Unverified TLD or suspicious domain length."}

    return {"url": url, "is_scam": False, "message": "SECURE: Domain verified and active."}

# --- THE AI CHAT ENGINE (STREAMING) ---
@app.post("/chat")
async def chat_handler(data: ChatInput):
    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "system", "content": "You are Nexora AI. Technical, elite, concise. Created by Naman Reddy."}, {"role": "user", "content": data.message}],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    return StreamingResponse(generate(), media_type="text/plain")
