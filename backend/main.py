import logging
import os
import re
import joblib
import tldextract
import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

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
def get_levenshtein_distance(s1, s2):
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

PROTECTED_BRANDS = [
    "paypal", "paytm", "phonepe", "gpay", "google", "sbi", "hdfc", "icici", "amazon", "flipkart", 
    "netflix", "facebook", "instagram", "whatsapp", "binance", "coinbase", "apple", "microsoft"
]

SUSPICIOUS_TLDS = ['.xyz', '.top', '.win', '.loan', '.club', '.online', '.site', '.biz', '.apk', '.app']

# --- THE SCANNER ENGINE (STRICT WATERFALL) ---
@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    
    # Clean URL for analysis
    ext = tldextract.extract(url)
    domain_primary = ext.domain  
    full_registered_domain = f"{ext.domain}.{ext.suffix}" 

    # GATE 1: BRAND SPOOFING (High Priority)
    for brand in PROTECTED_BRANDS:
        if brand in url:
            official_suffixes = [f"{brand}.com", f"{brand}.in", f"{brand}.net", f"{brand}.org", f"{brand}.co"]
            if not any(full_registered_domain == official for official in official_suffixes):
                return {
                    "url": url, "is_scam": True, "prediction_code": "BRAND_SPOOF",
                    "message": f"CRITICAL: Unauthorized use of {brand.upper()} identity."
                }
            return {"url": url, "is_scam": False, "message": "SECURE: Official brand domain verified."}

    # GATE 2: TYPOSQUATTING (Similarity)
    for brand in PROTECTED_BRANDS:
        distance = get_levenshtein_distance(domain_primary, brand)
        if 0 < distance <= 2:
            return {
                "url": url, "is_scam": True, "prediction_code": "SIMILARITY_THREAT",
                "message": f"CRITICAL: Visual imitation of {brand.upper()} detected."
            }

    # GATE 3: GIBBERISH / ENTROPY (Catching 'faaaah')
    # If the domain has 3+ repeating characters or no vowels, it's likely a scam
    if re.search(r'(.)\1\1', domain_primary) or len(domain_primary) > 4 and not any(v in domain_primary for v in 'aeiou'):
        return {
            "url": url, "is_scam": True, "prediction_code": "GIBBERISH_DETECTED",
            "message": "THREAT: Suspicious non-human domain string."
        }

    # GATE 4: PATTERN HEURISTICS
    if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}', url) or any(tld in url for tld in SUSPICIOUS_TLDS):
        return {"url": url, "is_scam": True, "prediction_code": "HIGH_RISK_PATTERN", "message": "THREAT: Malicious architecture/TLD."}
    
    if sum(c.isdigit() for c in url) > 9:
        return {"url": url, "is_scam": True, "prediction_code": "NUMERIC_OVERLOAD", "message": "THREAT: Excessive numeric characters."}

    # GATE 5: NEURAL INFERENCE (The Final Brain)
    if model:
        try:
            feat = [len(url), url.count('-'), url.count('.'), sum(c.isdigit() for c in url), 
                    len(re.findall(r'[^a-zA-Z0-9]', url)), 1 if 'https' in url else 0, 1]
            pred = model.predict([feat])[0]
            # Assuming 31 is your 'Safe' label. Anything else is a threat.
            if int(pred) != 31:
                return {"url": url, "is_scam": True, "prediction_code": str(pred), "message": "THREAT: Neural fraud signature matched."}
        except Exception as e:
            logger.error(f"Inference Error: {e}")

    return {"url": url, "is_scam": False, "message": "SECURE: No fraud signatures found."}

# --- THE AI CHAT ENGINE (STREAMING ENABLED) ---
@app.post("/chat")
async def chat_handler(data: ChatInput):
    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {"role": "system", "content": "You are Nexora AI, an elite security entity. Be concise and technical. No emojis."},
                {"role": "user", "content": data.message}
            ],
            stream=True 
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/plain")
