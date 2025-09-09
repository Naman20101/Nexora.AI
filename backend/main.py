import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import joblib
from typing import Optional
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

# This is a placeholder model for demonstration purposes.
# In a real application, you would load your trained model here.
def predict_fraud(feature1: float, feature2: float, feature3: float) -> int:
    """
    A simple, rule-based "model" to simulate fraud detection.
    This logic can be replaced with your actual machine learning model.
    """
    if feature1 > 0.8 or feature2 > 50 or feature3 < 0.1:
        return 1  # 1 indicates fraud
    else:
        return 0  # 0 indicates not fraud

class URLInput(BaseModel):
    url: HttpUrl

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
        url = str(data.url)
        # Simple rule-based check for the URL itself
        is_scam = False
        if re.search(r'verify-user', url, re.IGNORECASE) or re.search(r'login-', url, re.IGNORECASE):
            is_scam = True
        
        result = {"url": url, "is_scam": is_scam, "message": "OK"}
        return result
    except Exception as e:
        logging.exception("check-url failed")
        raise HTTPException(status_code=500, detail="Internal error")

@app.post("/predict")
def predict(data: SmallPredict):
    try:
        # Pass the features to the placeholder model
        pred = predict_fraud(data.feature1, data.feature2, data.feature3)
        
        return {"prediction": pred, "result": "Fraud" if pred == 1 else "Legit"}
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("predict failed")
        raise HTTPException(status_code=500, detail=str(e))
