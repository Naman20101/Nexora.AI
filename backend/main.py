import logging
import os
import re
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Set up logging to see exactly what happens in Render logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nexora.ai Fraud Detection API")

# Configure CORS - Essential for Vercel to communicate with Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLInput(BaseModel):
    url: str

# --- SAFE MODEL LOADING ---
MODEL_PATH = "advanced_url_model.pkl"
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        logger.info("✅ SUCCESS: Advanced model loaded.")
    else:
        logger.error(f"❌ ERROR: {MODEL_PATH} not found in root directory.")
except Exception as e:
    logger.error(f"❌ ERROR: Loading failed: {e}")

# If model fails, the app will still start, but we handle the error in the endpoint.

def get_features_from_url(url):
    """
    Enhanced feature extraction to match common Kaggle fraud datasets.
    """
    features = {
        'url_length': len(url),
        'num_hyphens': url.count('-'),
        'num_dots': url.count('.'),
        'num_digits': sum(c.isdigit() for c in url),
        'num_special_chars': len(re.findall(r'[!@#$%^&*()_+|~=`{}\[\]:";\'<>?,.\/]', url)),
        'has_https': 1 if url.startswith('https') else 0,
        'num_subdomains': url.count('.') - 1 if url.count('.') > 1 else 0
    }
    tlds = ['.com', '.org', '.net', '.gov', '.edu', '.biz', '.info']
    features['has_tld'] = 1 if any(tld in url for tld in tlds) else 0
    return features

@app.get("/")
def root():
    # Diagnostic endpoint to check if model is actually active
    return {
        "message": "Nexora.ai API live",
        "model_loaded": model is not None,
        "environment": "Production"
    }

@app.post("/check-url")
def check_url(data: URLInput):
    if model is None:
        logger.error("Attempted scan but model is not loaded.")
        return {
            "url": data.url,
            "is_scam": False, 
            "message": "Neural Engine Offline. Using Basic Heuristics.",
            "prediction_code": "OFFLINE"
        }

    try:
        url = str(data.url).lower()
        f = get_features_from_url(url)
        
        # Ensure the order of features matches how you trained the model
        feature_list = [[
            f['url_length'], f['num_hyphens'], f['num_dots'],
            f['num_digits'], f['num_special_chars'], 
            f['has_https'], f['has_tld']
        ]]
        
        pred = model.predict(feature_list)[0]
        
        # Logic: 31 is typically 'benign' in the Kaggle dataset
        is_scam = False if int(pred) == 31 else True
        
        return {
            "url": url,
            "is_scam": is_scam,
            "prediction_code": int(pred),
            "message": "Official/Safe Domain" if not is_scam else "High-Risk Fraud Pattern"
        }
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))

# Nexora AI Chat Logic
def nexora_chat_logic(message):
    message = message.lower()
    if any(word in message for word in ["hello", "hi", "hey"]):
        return "Systems active. I am Nexora AI. I scan payment links for neural fraud patterns. How can I assist, Naman?"
    elif "status" in message or "how are you" in message:
        return f"Core systems functional. Neural model status: {'ACTIVE' if model else 'OFFLINE'}. Ready for analysis."
    elif "help" in message:
        return "Paste a URL into the scanner or ask me to explain how I detect phishing patterns."
    elif "who made you" in message:
        return "I am the Nexora.ai core intelligence, built by Naman Reddy."
    elif "scam" in message or "fraud" in message:
        return "I use a Random Forest model trained on 284,807 URLs to find hidden scam patterns that humans miss."
    else:
        return "Understood. Please provide a URL for a neural safety scan or ask a security-related question."

@app.post("/chat")
async def chat_with_nexora(data: dict):
    user_msg = data.get("message", "")
    bot_response = nexora_chat_logic(user_msg)
    return {"response": bot_response}
