import logging
import re
import tldextract 
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Nexora Titan-Shield v9.RESTORATION")

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

# --- THE TOP NOTCH SECURITY CONSTANTS ---
INFRA_WHITELIST = r"(amazonaws\.com|azure\.com|windows\.net|googleusercontent\.com|firebaseapp\.com|github\.io|vercel\.app)"
TRUSTED_SITES = ["google.com", "amazon.com", "amazon.in", "microsoft.com", "apple.com", "github.com", "paypal.com", "facebook.com"]
PROTECTED_BRANDS = ["paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"]

@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # Normalize for Homograph Attacks (The PaypaI fix)
    normalized_url = url.replace('i', 'l').replace('1', 'l').replace('0', 'o')
    clean_domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    
    # 1. Trusted Bypass
    if re.search(INFRA_WHITELIST, clean_domain) or any(site == clean_domain for site in TRUSTED_SITES):
        return {"url": url, "is_scam": False, "message": "SECURE: Verified Domain."}

    # 2. Invalid Structure
    if "." not in clean_domain:
        return {"url": url, "is_scam": True, "message": "THREAT: Malformed URL."}

    # 3. Brand Identity Check (V9 Logic)
    for brand in PROTECTED_BRANDS:
        if brand in url or brand in normalized_url:
            if not any(brand in site for site in TRUSTED_SITES):
                return {"url": url, "is_scam": True, "message": f"CRITICAL: Unauthorized {brand.upper()} brand detected."}

    # 4. Gibberish & Entropy
    ext = tldextract.extract(url)
    domain_primary = ext.domain  
    if re.search(r'(.)\1\1\1', domain_primary): # Repetition check
        return {"url": url, "is_scam": True, "message": "THREAT: Malicious repetitive string."}

    if len(domain_primary) > 10:
        unique_ratio = len(set(domain_primary)) / len(domain_primary)
        if unique_ratio < 0.35:
            return {"url": url, "is_scam": True, "message": "THREAT: Gibberish/Keyboard Smash detected."}

    return {"url": url, "is_scam": False, "message": "Analysis complete: No fraud detected."}

@app.post("/chat")
async def chat_handler(data: ChatInput):
    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {"role": "system", "content": "You are Nexora AI. Built by Naman Reddy. Professional and concise."},
                {"role": "user", "content": data.message}
            ],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    return StreamingResponse(generate(), media_type="text/plain")
