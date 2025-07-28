from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pickle

# Load model
MODEL_PATH = "fraud_model.pkl"

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    raise RuntimeError(f"❌ Model loading failed: {e}")

# Initialize FastAPI app
app = FastAPI()

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Nexora.ai - A.AI.P.F.D.S backend is running.",
        "author": "Naman Reddy",
        "version": "v3.0"
    }

# Input schema
class TransactionInput(BaseModel):
    data: list  # Expecting 30 values: V1–V28, Time, Amount

# Prediction endpoint
@app.post("/predict")
def predict(input: TransactionInput):
    try:
        if len(input.data) != 30:
            raise ValueError("Expected 30 features (V1–V28, Time, Amount)")

        arr = np.array(input.data).reshape(1, -1)
        pred = model.predict(arr)[0]
        prob = model.predict_proba(arr)[0][1]  # Probability of fraud

        return {
            "prediction": int(pred),            # 0 = Legit, 1 = Fraud
            "probability_fraud": round(prob, 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

