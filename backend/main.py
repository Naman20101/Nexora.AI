import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import joblib
from typing import Optional

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Nexora.ai Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to load model safely
MODEL_PATH = "fraud_model.pkl"
model = None
try:
    model = joblib.load(MODEL_PATH)
    logging.info("Model loaded")
except Exception as e:
    logging.exception("Model load failed; continuing without model")

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
        # (your check logic here)
        result = {"url": url, "is_scam": False, "message": "OK"}
        return result
    except Exception as e:
        logging.exception("check-url failed")
        raise HTTPException(status_code=500, detail="Internal error")

@app.post("/predict")
def predict(data: SmallPredict):
    try:
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        X = [[data.feature1, data.feature2, data.feature3]]
        pred = int(model.predict(X)[0])
        return {"prediction": pred, "result": "Fraud" if pred == 1 else "Legit"}
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("predict failed")
        raise HTTPException(status_code=500, detail=str(e))
