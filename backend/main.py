import logging
import re
import tldextract 
import openai
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

# --- INITIALIZATION ---
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

# --- ADVANCED THREAT INTELLIGENCE ---
INFRA_WHITELIST = r"(amazonaws\.com|azure\.com|windows\.net|googleusercontent\.com|firebaseapp\.com|github\.io|vercel\.app)"
TRUSTED_DOMAINS = {"google.com", "amazon.com", "amazon.in", "microsoft.com", "apple.com", "github.com", "paypal.com", "facebook.com", "instagram.com"}
HIGH_RISK_TLDS = {".xyz", ".top", ".click", ".pw", ".info", ".gq", ".ml", ".cf", ".tk", ".ga", ".rest", ".tk", ".buzz", ".monster"}
PROTECTED_BRANDS = ["paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"]

def calculate_entropy(s):
    """Calculates Shannon Entropy to detect highly randomized strings."""
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return - sum([p * math.log(p) / math.log(2.0) for p in prob])

@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    clean_domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    
    # 1. ULTIMATE TRUSTED BYPASS
    if re.search(INFRA_WHITELIST, clean_domain) or any(site == clean_domain for site in TRUSTED_DOMAINS):
        return {"url": url, "is_scam": False, "message": "SECURE: Verified infrastructure."}

    # 2. MALFORMED STRUCTURE CHECK
    if "." not in clean_domain or len(clean_domain.split(".")[-1]) < 2:
        return {"url": url, "is_scam": True, "message": "CRITICAL: Malformed or invalid URL."}

    ext = tldextract.extract(url)
    dom = ext.domain
    full_tld = f".{ext.suffix}"

    # 3. RECURSIVE PATTERN ANALYSIS (INFINITE SENSITIVITY)
    
    # A. Suspicious TLD Block
    if full_tld in HIGH_RISK_TLDS:
        return {"url": url, "is_scam": True, "message": f"THREAT: High-risk TLD ({full_tld}) commonly used in phishing."}

    # B. Brand Identity Hijack (Enhanced)
    for brand in PROTECTED_BRANDS:
        if brand in url:
            if not any(brand in site for site in TRUSTED_DOMAINS):
                return {"url": url, "is_scam": True, "message": f"CRITICAL: Unauthorized use of {brand.upper()} brand."}

    # C. Advanced Repetition & Gibberish (Strict)
    # Flags 'Gabhhhh' or 'aaaa' patterns instantly
    if re.search(r'(.)\1\1', dom): 
        return {"url": url, "is_scam": True, "message": "THREAT: Malicious repetitive string (Gibberish)."}

    # D. Weighted Entropy & Unique Ratio Check
    # High entropy or low unique character ratio indicates keyboard smashing
    if len(dom) > 4:
        entropy = calculate_entropy(dom)
        unique_ratio = len(set(dom)) / len(dom)
        
        # Flag if randomized or highly repetitive spread-out chars
        if unique_ratio < 0.55 or entropy > 4.5:
            return {"url": url, "is_scam": True, "message": "THREAT: Neural scan suggests high-entropy malicious string."}

    # E. Homograph / Character Substitution Check
    # Catches things like 'g00gle' or mixing numbers into words suspiciously
    if re.search(r'[0-9]', dom) and len(dom) > 6:
        if not any(brand in dom for brand in ["365", "24", "4"]):
            return {"url": url, "is_scam": True, "message": "THREAT: Potential homograph/character substitution detected."}

    return {"url": url, "is_scam": False, "message": "Analysis complete: No fraud detected."}

@app.post("/chat")
async def chat_handler(data: ChatInput):
    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {"role": "system", "content": "You are Nexora.AI, a high-level security intelligence system built by Naman Reddy. Be technical and precise."},
                {"role": "user", "content": data.message}
            ],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content: yield chunk.choices[0].delta.content
    return StreamingResponse(generate(), media_type="text/plain")
