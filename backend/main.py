import logging
import re
import tldextract 
import openai
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
    is_voice: bool = False

AI_CLIENT = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# --- INFINITE SECURITY CONSTANTS ---
INFRA_WHITELIST = r"(amazonaws\.com|azure\.com|windows\.net|googleusercontent\.com|github\.io|vercel\.app)"
TRUSTED = ["google.com", "amazon.com", "amazon.in", "microsoft.com", "apple.com", "github.com", "paypal.com"]
SUSPICIOUS_TLDS = [".xyz", ".top", ".click", ".pw", ".info", ".gq", ".ml", ".cf", ".tk"]

@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    clean_domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    
    # 1. THE ULTIMATE BYPASS (Trusted only)
    if re.search(INFRA_WHITELIST, clean_domain) or any(site == clean_domain for site in TRUSTED):
        return {"is_scam": False, "message": "SECURE: Verified infrastructure."}

    # 2. MALFORMED CHECK
    if "." not in clean_domain:
        return {"is_scam": True, "message": "CRITICAL: Malformed URL structure."}

    ext = tldextract.extract(url)
    dom = ext.domain
    full_ext = f".{ext.suffix}"

    # 3. SUSPICIOUS TLD BLOCKER
    if full_ext in SUSPICIOUS_TLDS:
        return {"is_scam": True, "message": f"THREAT: High-risk extension ({full_ext}) detected."}

    # 4. GIBBERISH & ENTROPY (ULTRA-STRICT)
    # Flags if unique characters are less than 60% of total length
    if len(dom) > 3:
        unique_ratio = len(set(dom)) / len(dom)
        if unique_ratio < 0.60 or re.search(r'(.)\1\1', dom):
            return {"is_scam": True, "message": "THREAT: Neural patterns suggest gibberish/smash."}

    # 5. HOMOGRAPH/LOOKALIKES
    # Flags numbers mixed with letters in suspicious ways
    if any(char.isdigit() for char in dom) and len(dom) > 5:
        if not any(brand in dom for brand in ["365", "4", "24"]):
            return {"is_scam": True, "message": "THREAT: Suspicious character substitution detected."}

    return {"is_scam": False, "message": "Analysis complete: No fraud detected."}

@app.post("/chat")
async def chat_handler(data: ChatInput):
    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {"role": "system", "content": "Identity: Nexora.AI. Creator: Naman Reddy. Mode: Professional/Neutral. Only call user Naman if verified."},
                {"role": "user", "content": data.message}
            ],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    return StreamingResponse(generate(), media_type="text/plain")
