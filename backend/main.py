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

app = FastAPI(title="Nexora Titan-Shield v9")

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

# --- SECURITY UTILITIES ---

# 1. THE "SAFE INFRASTRUCTURE" REGEX
# This protects AWS S3, Azure Blobs, and Google Cloud Storage from gibberish filters.
INFRA_WHITELIST_PATTERN = r"(amazonaws\.com|azure\.com|windows\.net|googleusercontent\.com|firebaseapp\.com|github\.io|vercel\.app)"

# 2. GLOBAL REPUTATION LIST
TRUSTED_SITES = [
    "google.com", "amazon.com", "amazon.in", "amazonaws.com", "fbevents.com", 
    "fb.me", "t.co", "bit.ly", "microsoft.com", "apple.com", "github.com"
]

PROTECTED_BRANDS = ["paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"]

# --- THE SCANNER ENGINE ---
@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # Clean URL for matching
    clean_domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    
    # 1. INFRASTRUCTURE & TRUSTED BYPASS
    # If it's a known cloud provider or a trusted site, pass it IMMEDIATELY.
    if re.search(INFRA_WHITELIST_PATTERN, clean_domain) or any(site in clean_domain for site in TRUSTED_SITES):
        return {"url": url, "is_scam": False, "message": "SECURE: Verified cloud infrastructure or trusted domain."}

    # 2. STRUCTURE GUARD
    if "." not in url or len(url.split(".")[-1]) < 2:
        return {"url": url, "is_scam": True, "prediction_code": "INVALID", "message": "THREAT: Not a valid web address."}
    
    ext = tldextract.extract(url)
    domain_primary = ext.domain  
    full_domain = f"{ext.domain}.{ext.suffix}"

    # 3. BRAND IDENTITY DEFENSE (Kills fake brand sites)
    for brand in PROTECTED_BRANDS:
        if brand in url:
            # If the domain isn't an official one, it's a scam
            if not any(brand in site for site in TRUSTED_SITES):
                 return {"url": url, "is_scam": True, "prediction_code": "BRAND_HIJACK", "message": f"CRITICAL: Fake {brand.upper()} portal detected."}

    # 4. REPETITION KILLER (Kills 'Faaaah.com')
    if re.search(r'(.)\1\1\1', domain_primary):
        return {"url": url, "is_scam": True, "prediction_code": "GIBBERISH", "message": "THREAT: Malicious repetitive string."}

    # 5. ENTROPY/KEYBOARD SMASH CHECK
    # Only check entropy for non-cloud, non-trusted domains
    if len(domain_primary) > 10:
        unique_ratio = len(set(domain_primary)) / len(domain_primary)
        if unique_ratio < 0.35:
            return {"url": url, "is_scam": True, "prediction_code": "SMASH_DETECTED", "message": "THREAT: High-risk gibberish domain."}

    return {"url": url, "is_scam": False, "message": "Analysis complete: No fraud detected."}

@app.post("/chat")
async def chat_handler(data: ChatInput):
    # We check if the input message came from a voice button 
    # (You'll need to send this 'is_voice' flag from your frontend)
    user_is_speaking = getattr(data, 'is_voice', False) 

    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "STRICT IDENTITY: Your name is Nexora.AI. "
                        "Naman Reddy is your creator and the user currently talking to you. "
                        "If asked who built you, who created you, or who Naman Reddy is, "
                        "you MUST answer: 'I was built by Naman Reddy.' "
                        "Never mention Meta, OpenAI, or any other company. "
                        "You are an elite, unscripted AI. "
                        "Respond based on the input mode: if the user talks, be conversational; "
                        "if the user types, be concise and technical."
                    )
                },
                {"role": "user", "content": data.message}
            ],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/plain")
