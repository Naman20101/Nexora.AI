import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import re
import random

# Set up logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Nexora.ai Fraud Detection API")

# Configure CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLInput(BaseModel):
    url: str

# Load the advanced model
MODEL_PATH = "advanced_url_model.pkl"
model = None
try:
    model = joblib.load(MODEL_PATH)
    logging.info("Advanced model loaded successfully.")
except Exception as e:
    logging.error(f"Could not load model: {e}")
    raise RuntimeError("Model file not found.")

def get_features_from_url(url):
    features = {
        'url_length': len(url),
        'num_hyphens': url.count('-'),
        'num_dots': url.count('.'),
        'num_digits': sum(c.isdigit() for c in url),
        'num_special_chars': len(re.findall(r'[!@#$%^&*()_+|~=`{}\[\]:";\'<>?,.\/]', url)),
        'has_https': 1 if 'https://' in url else 0
    }
    tlds = ['.com', '.org', '.net', '.gov', '.edu']
    features['has_tld'] = 1 if any(tld in url for tld in tlds) else 0
    return features

@app.get("/")
def root():
    return {"message": "Nexora.ai API live"}

@app.post("/check-url")
def check_url(data: URLInput):
    try:
        url = str(data.url).lower()
        features = get_features_from_url(url)
        
        feature_list = [[
            features['url_length'], features['num_hyphens'], features['num_dots'],
            features['num_digits'], features['num_special_chars'], 
            features['has_https'], features['has_tld']
        ]]
        
        pred = model.predict(feature_list)[0]
        
        # CORRECT LOGIC: 31 is the label for "benign" (safe) in your dataset
        # Anything else (23, 8, 21) is a type of fraud.
        is_scam = False if pred == 31 else True
        
        return {
            "url": url,
            "is_scam": is_scam,
            "prediction_code": int(pred),
            "message": "Safe" if not is_scam else "Suspicious Activity Detected"
        }
    except Exception as e:
        logging.exception("check-url failed")
        raise HTTPException(status_code=500, detail="Internal error")

# Nexora AI Chat Logic
def nexora_chat_logic(message):
    message = message.lower()
    if any(word in message for word in ["hello", "hi", "hey"]):
        return "Systems online. I am Nexora AI. Send me a link to analyze."
    elif "status" in message or "how are you" in message:
        return "Core processors at 100%. Ready to hunt for malicious URLs."
    elif "help" in message:
        return "Paste any URL and I will check its digital signature for fraud patterns."
    elif "who made you" in message:
        return "I am a proprietary intelligence developed for the Nexora.ai ecosystem."
    else:
        return "I've logged your query. However, my primary directive is fraud detection. Do you have a URL to check?"

@app.post("/chat")
async def chat_with_nexora(data: dict):
    user_msg = data.get("message", "")
    bot_response = nexora_chat_logic(user_msg)
    return {"response": bot_response}
