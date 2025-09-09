import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import re

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Nexora.ai Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is a placeholder for your trained model.
# You would need to train a model on a dataset and save it as this file.
MODEL_PATH = "fraud_model.pkl"
model = None
try:
    model = joblib.load(MODEL_PATH)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.warning(f"Could not load model: {e}")
    model = "placeholder" # Use a placeholder if the model is not found

class URLInput(BaseModel):
    url: str

class SmallPredict(BaseModel):
    feature1: float
    feature2: float
    feature3: float

@app.get("/")
def root():
    return {"message": "Nexora.ai API live"}

@app.post("/check-url")
def check_url(data: URLInput):
    try:
        url = str(data.url).lower()
        is_scam = False
        
        # Make the URL a proper one if it's missing http://
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        # This is a list of known brand names for common scam targeting
        brand_names = ['paypal', 'google', 'amazon', 'apple', 'microsoft']

        # This is a list of suspicious words and characters
        suspicious_words = ['verify', 'login', 'account', 'secure', 'update', 'confirm', 'access', 'id', 'password', 'reset', 'sign-in']
        suspicious_tlds = ['.ru', '.cn', '.xyz', '.tk', '.ga', '.ml', '.cf', '.gq', '.pw']
        
        # Check for multiple suspicious words or a combination of a brand and a suspicious word
        if any(brand in url for brand in brand_names) and any(word in url for word in suspicious_words):
            is_scam = True
            
        # Check if the domain is a subdomain of a suspicious TLD
        for tld in suspicious_tlds:
            if tld in url:
                is_scam = True
                break
        
        # Check for common typos (e.g., paypa1, amaz0n)
        if re.search(r'paypa1|amaz0n|goog1e', url):
            is_scam = True

        # Check for excessive subdomains (e.g., login.verify.paypal.com)
        if len(url.split('.')) > 5:
            is_scam = True
        
        result = {"url": url, "is_scam": is_scam, "message": "OK"}
        return result
    except Exception as e:
        logging.exception("check-url failed")
        raise HTTPException(status_code=500, detail="Internal error")

@app.post("/predict")
def predict(data: SmallPredict):
    try:
        if model == "placeholder":
            # Simple rule for the placeholder model
            if data.feature1 > 0.8:
                pred = 1
            else:
                pred = 0
        else:
            # This is where your actual model prediction would go.
            # Replace this with the code that uses your loaded model.
            X = [[data.feature1, data.feature2, data.feature3]]
            pred = int(model.predict(X)[0])
        
        return {"prediction": pred, "result": "Fraud" if pred == 1 else "Legit"}
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("predict failed")
        raise HTTPException(status_code=500, detail=str(e))
