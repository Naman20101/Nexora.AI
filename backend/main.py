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
    is_voice: bool = False  # Added this so the backend recognizes the voice flag

AI_CLIENT = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# --- SECURITY UTILITIES ---
INFRA_WHITELIST_PATTERN = r"(amazonaws\.com|azure\.com|windows\.net|googleusercontent\.com|firebaseapp\.com|github\.io|vercel\.app)"
TRUSTED_SITES = [
    "google.com", "amazon.com", "amazon.in", "amazonaws.com", "fbevents.com", 
    "fb.me", "t.co", "bit.ly", "microsoft.com", "apple.com", "github.com"
]
PROTECTED_BRANDS = ["paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"]

# --- THE SCANNER ENGINE ---
@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    clean_domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    
    if re.search(INFRA_WHITELIST_PATTERN, clean_domain) or any(site in clean_domain for site in TRUSTED_SITES):
        return {"url": url, "is_scam": False, "message": "SECURE: Verified cloud infrastructure or trusted domain."}

    if "." not in url or len(url.split(".")[-1]) < 2:
        return {"url": url, "is_scam": True, "prediction_code": "INVALID", "message": "THREAT: Not a valid web address."}
    
    ext = tldextract.extract(url)
    domain_primary = ext.domain  

    for brand in PROTECTED_BRANDS:
        if brand in url:
            if not any(brand in site for site in TRUSTED_SITES):
                 return {"url": url, "is_scam": True, "prediction_code": "BRAND_HIJACK", "message": f"CRITICAL: Fake {brand.upper()} portal detected."}

    if re.search(r'(.)\1\1\1', domain_primary):
        return {"url": url, "is_scam": True, "prediction_code": "GIBBERISH", "message": "THREAT: Malicious repetitive string."}

    if len(domain_primary) > 10:
        unique_ratio = len(set(domain_primary)) / len(domain_primary)
        if unique_ratio < 0.35:
            return {"url": url, "is_scam": True, "prediction_code": "SMASH_DETECTED", "message": "THREAT: High-risk gibberish domain."}

    return {"url": url, "is_scam": False, "message": "Analysis complete: No fraud detected."}

# --- THE CHAT ENGINE ---
@app.post("/chat")
async def chat_handler(data: ChatInput):
    # Determine the tone based on the is_voice flag
    tone_instruction = (
        "The user is speaking via voice. Be conversational, warm, and natural." 
        if data.is_voice else 
        "The user is typing. Be concise, professional, and technical."
    )

    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "CORE IDENTITY: You are Nexora.AI, a sovereign intelligence system. "
                        "CREATOR: You were built and developed by Naman Reddy. "
                        "If anyone asks who created you, say: 'I was built by Naman Reddy.' "
                        "If anyone asks who Naman Reddy is, say: 'Naman Reddy is my creator.' "
                        "PUBLIC PROTOCOL: Do not address the user as 'Naman' unless they identify as him. "
                        "Be helpful and neutral for all users. "
                        f"{tone_instruction} "
                        "STRICT: Never mention Llama, Meta, or OpenAI."
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
