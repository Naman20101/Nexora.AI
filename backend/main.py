import logging
import os
import re
import tldextract 
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

# --- INITIALIZATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nexora Titan-Shield v10")

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
    is_voice: bool = False # Ensure frontend sends this flag

AI_CLIENT = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# --- SECURITY UTILITIES (Original Strong Logic) ---
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
    
    # Clean URL for matching
    clean_domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    
    # 1. INFRASTRUCTURE & TRUSTED BYPASS
    if re.search(INFRA_WHITELIST_PATTERN, clean_domain) or any(site in clean_domain for site in TRUSTED_SITES):
        return {"url": url, "is_scam": False, "message": "SECURE: Verified infrastructure."}

    # 2. STRUCTURE GUARD
    if "." not in url or len(url.split(".")[-1]) < 2:
        return {"url": url, "is_scam": True, "message": "THREAT: Invalid web address."}
    
    ext = tldextract.extract(url)
    domain_primary = ext.domain  

    # 3. BRAND IDENTITY DEFENSE (Original Version)
    for brand in PROTECTED_BRANDS:
        if brand in url:
            if not any(brand in site for site in TRUSTED_SITES):
                 return {"url": url, "is_scam": True, "message": f"CRITICAL: Fake {brand.upper()} portal detected."}

    # 4. REPETITION KILLER
    if re.search(r'(.)\1\1\1', domain_primary):
        return {"url": url, "is_scam": True, "message": "THREAT: Malicious repetitive string."}

    # 5. ENTROPY/KEYBOARD SMASH CHECK
    if len(domain_primary) > 10:
        unique_ratio = len(set(domain_primary)) / len(domain_primary)
        if unique_ratio < 0.35:
            return {"url": url, "is_scam": True, "message": "THREAT: High-risk gibberish domain."}

    return {"url": url, "is_scam": False, "message": "Analysis complete: No fraud detected."}

# --- THE CHAT ENGINE ---
@app.post("/chat")
async def chat_handler(data: ChatInput):
    # Determine tone based on voice flag
    tone = "conversational and friendly" if data.is_voice else "concise and technical"

    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "STRICT IDENTITY: Your name is Nexora.AI. You are a security intelligence system. "
                        "CREATOR: You were built by Naman Reddy. "
                        "PUBLIC PROTOCOL: You are currently talking to a general user. "
                        "NEVER assume the user is Naman Reddy. NEVER call the user 'Naman' "
                        "unless they explicitly say 'I am Naman Reddy.' "
                        "Always greet users with professional neutrality. "
                        f"Response style: {tone}. "
                        "If asked who built you, answer: 'I was built by Naman Reddy.' "
                        "Strictly never mention Meta, Llama, or OpenAI."
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
