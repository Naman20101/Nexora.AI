# pyright: reportMissingImports=false

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle

# Load the trained model
with open("fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

app = FastAPI(
    title="Nexora.ai (A.AI.P.F.D.S)",
    description="An AI-powered fraud detection system that analyzes transaction patterns and detects anomalies in real-time. Developed by Naman Reddy.",
    version="v3.0"
)

# Pydantic model for input validation
class Transaction(BaseModel):
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Nexora.ai (A.AI.P.F.D.S) - Fraud Detection API 🚀",
        "author": "Naman Reddy",
        "version": "v3.0"
    }

@app.post("/predict")
def predict_fraud(transaction: Transaction):
    try:
        features = [[
            transaction.amount,
            transaction.oldbalanceOrg,
            transaction.newbalanceOrig
        ]]
        prediction = model.predict(features)[0]
        result = "Fraudulent Transaction ⚠️" if prediction == 1 else "Legitimate Transaction ✅"
        return {
            "prediction": int(prediction),
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


