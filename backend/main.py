import logging
import os
import re
import joblib
import tldextract 
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

# --- INITIALIZATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nexora Titan-Shield Balanced")

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
except: pass

# --- SECURITY UTILITIES ---

# 1. EXPANDED TRUST LIST (Common legitimate domains)
TRUSTED_SITES = [
    "google.com", "google.in", "apple.com", "amazon.in", "amazon.com", 
    "facebook.com", "fb.me", "fbevents.com", "instagram.com", "whatsapp.com",
    "microsoft.com", "github.com", "t.co", "bit.ly", "netflix.com"
]

PROTECTED_BRANDS = ["paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"]

# --- THE SCANNER ENGINE ---
@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # Clean URL for matching
    clean_domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    
    # 1. TRUSTED SITE BYPASS (The "Don't touch the big guys" rule)
    if clean_domain in TRUSTED_SITES:
        return {"url": url, "is_scam": False, "message": "SECURE: Official verified domain."}

    # 2. STRUCTURE CHECK (Kills 'Nahbri' or 'Imsafw')
    if "." not in url or len(url.split(".")[-1]) < 2:
        return {"url": url, "is_scam": True, "prediction_code": "INVALID", "message": "THREAT: Not a valid web address."}
    
    ext = tldextract.extract(url)
    domain_primary = ext.domain  
    full_domain = f"{ext.domain}.{ext.suffix}"

    # 3. BRAND IDENTITY DEFENSE (Kills fake brand sites)
    for brand in PROTECTED_BRANDS:
        if brand in url:
            # If the domain isn't one of our known trusted domains for that brand
            if not any(brand in site for site in TRUSTED_SITES):
                 return {"url": url, "is_scam": True, "prediction_code": "BRAND_HIJACK", "message": f"CRITICAL: Fake {brand.upper()} portal detected."}

    # 4. REPETITION KILLER (Kills 'Faaaah.com')
    if re.search(r'(.)\1\1\1', domain_primary):
        return {"url": url, "is_scam": True, "prediction_code": "GIBBERISH", "message": "THREAT: Malicious repetitive string."}

    # 5. ENTROPY/KEYBOARD SMASH CHECK
    # Checks if the domain name has enough unique characters to be a real word
    if len(domain_primary) > 7:
        unique_ratio = len(set(domain_primary)) / len(domain_primary)
        if unique_ratio < 0.4:
            return {"url": url, "is_scam": True, "prediction_code": "SMASH_DETECTED", "message": "THREAT: High-risk gibberish domain."}

    # 6. NEURAL INFERENCE (The backup AI)
    if model:
        try:
            feat = [len(url), url.count('-'), url.count('.'), sum(c.isdigit() for c in url), len(re.findall(r'[^a-zA-Z0-9]', url)), 1 if 'https' in url else 0, 1]
            pred = model.predict([feat])[0]
            if int(pred) != 31:
                 return {"url": url, "is_scam": True, "prediction_code": "AI_FLAG", "message": "THREAT: Potential fraud signature matched."}
        except: pass

    # If it passes all the above, we consider it safe for now
    return {"url": url, "is_scam": False, "message": "Analysis complete: No fraud detected."}

# --- THE AI CHAT ENGINE ---
@app.post("/chat")
async def chat_handler(data: ChatInput):
    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "system", "content": "You are Nexora AI. Concise and elite."}, {"role": "user", "content": data.message}],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content: yield chunk.choices[0].delta.content
    return StreamingResponse(generate(), media_type="text/plain")
