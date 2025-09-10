import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import re
import requests
import ipaddress

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

def get_features_from_url(url):
    """
    Extracts a number of features from a given URL.
    This is what your model would be trained on.
    """
    
    # Check if a domain has an IP address instead of a name
    is_ip = 0
    try:
        ipaddress.ip_address(url.split('//')[-1].split('/')[0])
        is_ip = 1
    except ValueError:
        pass
        
    features = {
        "length_of_url": len(url),
        "num_dots_in_url": url.count('.'),
        "has_at_symbol": 1 if '@' in url else 0,
        "is_ip_address": is_ip,
        "num_dashes": url.count('-'),
        "num_http": url.count('http'),
        "num_redirects": 0 # This would be a feature from the requests library
    }
    
    return features

@app.post("/check-url")
def check_url(data: URLInput):
    try:
        url = str(data.url).lower()
        
        # This is where we would use a real trained model
        # For now, we'll return the features and a placeholder prediction
        
        features = get_features_from_url(url)
        
        # Example prediction based on one feature
        is_scam = True if features['num_dots_in_url'] > 3 else False
        
        result = {
            "url": url,
            "is_scam": is_scam,
            "details": features,
            "message": "OK"
        }
        
        return result
    except Exception as e:
        logging.exception("check-url failed")
        raise HTTPException(status_code=500, detail="Internal error")

@app.post("/predict")
def predict(data: SmallPredict):
    try:
        if model == "placeholder":
            if data.feature1 > 0.8:
                pred = 1
            else:
                pred = 0
        else:
            X = [[data.feature1, data.feature2, data.feature3]]
            pred = int(model.predict(X)[0])
        
        return {"prediction": pred, "result": "Fraud" if pred == 1 else "Legit"}
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("predict failed")
        raise HTTPException(status_code=500, detail=str(e))
