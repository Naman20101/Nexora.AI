from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import joblib
import numpy as np

app = FastAPI()

# Input schema
class Transaction(BaseModel):
    data: List[float]  # expects 30 float features

# Load model
model = None
try:
    model = joblib.load("fraud_model.pkl")
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Model loading failed: {e}")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Fraud Detection API is running."}

# Prediction endpoint
@app.post("/predict")
def predict(transaction: Transaction):
    if model is None:
        return {"status": "Model not loaded"}
    
    if len(transaction.data) != 30:
        return {"error": "Exactly 30 features are required."}

    try:
        input_array = np.array(transaction.data).reshape(1, -1)
        prediction = model.predict(input_array)[0]
        return {"prediction": int(prediction)}
    except Exception as e:
        return {"error": str(e)}



