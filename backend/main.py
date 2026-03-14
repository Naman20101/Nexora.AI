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
    is_voice: bool = False 

AI_CLIENT = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# --- SECURITY UTILITIES ---
INFRA_WHITELIST_PATTERN = r"(amazonaws\.com|azure\.com|windows\.net|googleusercontent\.com|firebaseapp\.com|github\.io|vercel\.app)"
TRUSTED_SITES = ["google.com", "amazon.com", "amazon.in", "github.com", "microsoft.com", "apple.com"]
PROTECTED_BRANDS = ["paypal", "paytm", "phonepe", "gpay", "sbi", "hdfc", "binance", "netflix"]

@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url).lower().strip()
    clean_domain = re.sub(r'^https?://(www\.)?', '', url).split('/')[0]
    
    if re.search(INFRA_WHITELIST_PATTERN, clean_domain) or any(site in clean_domain for site in TRUSTED_SITES):
        return {"is_scam": False, "message": "SECURE: Verified infrastructure."}

    for brand in PROTECTED_BRANDS:
        if brand in url and not any(brand in site for site in TRUSTED_SITES):
            return {"is_scam": True, "message": f"CRITICAL: Fake {brand.upper()} portal detected."}

    return {"is_scam": False, "message": "Analysis complete: No fraud detected."}

@app.post("/chat")
async def chat_handler(data: ChatInput):
    # Tone logic
    tone = "conversational and friendly" if data.is_voice else "concise and technical"
    
    def generate():
        stream = AI_CLIENT.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are Nexora.AI, a security intelligence system created by Naman Reddy. "
                        "When talking to users, be professional and neutral. Do not call them 'Naman' "
                        "unless they introduce themselves as him. "
                        f"Your response style should be {tone}. "
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
