from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# Define input schema
class TransactionData(BaseModel):
    features: list  # Expecting a list of 30 numeric features

# Load model
try:
    model = joblib.load("fraud_model.pkl")
except Exception as e:
    raise RuntimeError(f"❌ Model loading failed: {e}")

@app.get("/")
def read_root():
    return {"message": "✅ Fraud Detection API is running!"}

@app.post("/predict")
def predict(data: TransactionData):
    try:
        input_data = np.array(data.features).reshape(1, -1)
        prediction = model.predict(input_data)[0]
        return {"prediction": int(prediction)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

from fastapi import FastAPI
from safe_check import router as safe_check_router  # ✅ Add this

app = FastAPI()

# Include the safe link checker route
app.include_router(safe_check_router)  # ✅ Add this line

# (Other routes if you already have them)
from pydantic import BaseModel
import requests

# Model to receive the URL
class URLCheckRequest(BaseModel):
    url: str

# Function to check for scam indicators
def is_scam_url(url: str) -> bool:
    suspicious_keywords = [
        "free", "gift", "claim", "verify", "login", "update", "secure",
        "account", "pay", "wallet", "bank", "click", "offer", "win", "bonus"
    ]
    try:
        response = requests.get(url, timeout=5)
        content = response.text.lower()
        for keyword in suspicious_keywords:
            if keyword in content:
                return True
        return False
    except Exception:
        # If the URL can't be reached or fails, treat it as suspicious
        return True

# API endpoint for URL checking
@app.post("/check-url")
def check_url(data: URLCheckRequest):
    url = data.url
    scam = is_scam_url(url)
    return {
        "url": url,
        "is_scam": scam,
        "message": "Scam detected!" if scam else "URL seems safe."
    }