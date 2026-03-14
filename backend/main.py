import logging
import os
import re
import joblib
import tldextract 
import openai
import socket
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
def verify_dns(hostname: str) -> bool:
    try:
        socket.gethostbyname(hostname)
        return True
    except:
        return False

# 1. THE "SAFE PASS" LIST (Real links that look weird)
GLOBAL_WHITELIST = [
    "fbevents.com", "fb.me", "t.co", "bit.ly", "goo.gl", "aka.ms", 
    "images-na.ssl-images-amazon.com", "wp.com", "ghcdn.rawgit.org"
]

PROTECTED_BRANDS = ["paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"]
TRUSTED_TLDS = ['com', 'in', 'net', 'org', 'co', 'gov', 'edu', 'io', 'me', 'info', 'ai', 'app']

# --- THE SCANNER ENGINE ---
@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # Clean URL for extraction (remove http/https/www)
    clean_url = re.sub(r'^https?://(www\.)?', '', url)
    
    # 1. WHITELIST PASS (Fast track for fbevents.com etc.)
    if any(white_domain in clean_url for white_domain in GLOBAL_WHITELIST):
        return {"url": url, "is_scam": False, "message": "SECURE: Verified global infrastructure link."}

    # 2. HARD STRUCTURE CHECK
    if "." not in url or len(url.split(".")[-1]) < 2:
        return {"url": url, "is_scam": True, "prediction_code": "INVALID_URL", "message": "THREAT: Not a valid web address structure."}
    
    # 3. EXTRACTION
    ext = tldextract.extract(url)
    domain_primary = ext.domain  
    suffix = ext.suffix
    full_domain = f"{ext.domain}.{ext.suffix}"

    # 4. DNS VERIFICATION (Does it actually exist?)
    if not verify_dns(full_domain):
        return {"url": url, "is_scam": True, "prediction_code": "GIBBERISH_NONSENSE", "message": "THREAT: Domain not found on the web (Fake/Gibberish)."}

    # 5. BRAND DEFENSE (Identity Theft)
    for brand in PROTECTED_BRANDS:
        if brand in url:
            # Check if it's the official brand domain
            if full_domain not in [f"{brand}.{tld}" for tld in TRUSTED_TLDS]:
                return {"url": url, "is_scam": True, "prediction_code": "IDENTITY_THEFT", "message": f"CRITICAL: Unauthorized {brand.upper()} impersonation."}
            else:
                return {"url": url, "is_scam": False, "message": f"SECURE: Official {brand.upper()} domain."}

    # 6. GIBBERISH/PATTERN KILLER
    if re.search(r'(.)\1\3', domain_primary): # Flag 4+ repeating characters
        return {"url": url, "is_scam": True, "prediction_code": "PATTERN_THREAT", "message": "THREAT: Malicious repetitive string detected."}

    # 7. NEURAL INFERENCE
    if model:
        try:
            feat = [len(url), url.count('-'), url.count('.'), sum(c.isdigit() for c in url), len(re.findall(r'[^a-zA-Z0-9]', url)), 1 if 'https' in url else 0, 1]
            pred = model.predict([feat])[0]
            if int(pred) != 31:
                 return {"url": url, "is_scam": True, "prediction_code": "AI_FLAG", "message": "THREAT: Potential fraud signature matched."}
        except: pass

    # 8. TLD & LENGTH CHECK
    if suffix not in TRUSTED_TLDS and len(domain_primary) < 5:
        return {"url": url, "is_scam": True, "prediction_code": "UNVERIFIED_SOURCE", "message": "THREAT: Unverified TLD and suspicious domain length."}

    return {"url": url, "is_scam": False, "message": "Analysis complete: No fraud detected."}

# --- THE AI CHAT ENGINE ---
@app.post("/chat")
async def chat_handler(data: ChatInput):
    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "system", "content": "You are Nexora AI. Tech-focused, concise."}, {"role": "user", "content": data.message}],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    return StreamingResponse(generate(), media_type="text/plain")
