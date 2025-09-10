import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import re
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

MODEL_PATH = "fraud_model.pkl"
model = None
try:
    model = joblib.load(MODEL_PATH)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Could not load model: {e}")
    raise RuntimeError("Model file not found or corrupted.")

class URLInput(BaseModel):
    url: str

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
        domain = url.split('//')[-1].split('/')[0].split(':')[0]
        ipaddress.ip_address(domain)
        is_ip = 1
    except (ValueError, IndexError):
        pass
        
    features = {
        "length_of_url": len(url),
        "num_dots_in_url": url.count('.'),
        "has_at_symbol": 1 if '@' in url else 0,
        "is_ip_address": is_ip,
        "num_dashes": url.count('-'),
    }
    
    return features

@app.post("/check-url")
def check_url(data: URLInput):
    try:
        url = str(data.url).lower()
        
        # Get the features from the URL
        features = get_features_from_url(url)
        
        # Convert features to a format the model can use
        feature_list = [[
            features['length_of_url'], 
            features['num_dots_in_url'], 
            features['has_at_symbol'], 
            features['is_ip_address'], 
            features['num_dashes']
        ]]
        
        # Use the trained model to make a prediction
        pred = model.predict(feature_list)[0]
        is_scam = bool(pred)
        
        result = {
            "url": url,
            "is_scam": is_scam,
            "details": features,
            "message": "Prediction made by ML model"
        }
        
        return result
    except Exception as e:
        logging.exception("check-url failed")
        raise HTTPException(status_code=500, detail="Internal error")

# The predict endpoint is now fully functional with the model
@app.post("/predict")
def predict(data: SmallPredict):
    try:
        X = [[data.feature1, data.feature2, data.feature3]]
        pred = int(model.predict(X)[0])
        
        return {"prediction": pred, "result": "Fraud" if pred == 1 else "Legit"}
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("predict failed")
        raise HTTPException(status_code=500, detail=str(e))
