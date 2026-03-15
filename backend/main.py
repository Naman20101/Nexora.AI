import logging
import re
import tldextract 
import openai
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Nexora Titan-Shield v11.INFINITE")

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

# --- INFINITE INTELLIGENCE ---
INFRA_WHITELIST = r"(amazonaws\.com|azure\.com|windows\.net|googleusercontent\.com|github\.io|vercel\.app)"
TRUSTED_DOMAINS = {"google.com", "amazon.com", "amazon.in", "microsoft.com", "apple.com", "github.com", "paypal.com", "facebook.com"}
PROTECTED_BRANDS = ["paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "netflix", "binance"]

@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # 1. CLEANING & NORMALIZATION
    # This converts "paypai" (with uppercase I) to standard "paypai" for checking
    normalized_url = url.replace('i', 'l').replace('1', 'l').replace('0', 'o')
    clean_domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    
    # 2. TRUSTED BYPASS
    if re.search(INFRA_WHITELIST, clean_domain) or any(site == clean_domain for site in TRUSTED_DOMAINS):
        return {"is_scam": False, "message": "SECURE: Verified infrastructure."}

    # 3. INFINITE BRAND PROTECTION (The "PaypaI" Fix)
    # We check both the raw URL and the normalized URL for brand names
    for brand in PROTECTED_BRANDS:
        if brand in url or brand in normalized_url:
            # If the brand is present but the domain isn't the official one:
            if not any(brand in site for site in TRUSTED_DOMAINS):
                return {"is_scam": True, "message": f"CRITICAL: Unauthorized {brand.upper()} impersonation detected."}

    # 4. SUSPICIOUS KEYWORDS + UNTRUSTED DOMAIN
    # Flags words like 'verify', 'login', 'secure' if they aren't on Google/Amazon
    scam_keywords = ["verify", "login", "update", "secure", "account", "banking"]
    if any(word in url for word in scam_keywords):
        return {"is_scam": True, "message": "THREAT: Suspicious credential-harvesting pattern."}

    # 5. GIBBERISH & REPETITION
    ext = tldextract.extract(url)
    dom = ext.domain
    if re.search(r'(.)\1\1', dom) or (len(set(dom)) / len(dom) < 0.55 if len(dom) > 4 else False):
        return {"is_scam": True, "message": "THREAT: Malicious gibberish/entropy detected."}

    return {"is_scam": False, "message": "Analysis complete: No fraud detected."}

@app.post("/chat")
async def chat_handler(data: ChatInput):
    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {"role": "system", "content": "You are Nexora.AI, a security system built by Naman Reddy. Technical and neutral."},
                {"role": "user", "content": data.message}
            ],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content: yield chunk.choices[0].delta.content
    return StreamingResponse(generate(), media_type="text/plain")
