from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import traceback
import os

app = FastAPI()

class Transaction(BaseModel):
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float

# Load the model
try:
    model = joblib.load("fraud_model.pkl")
except Exception as e:
    print("❌ Error loading model:", e)
    traceback.print_exc()
    model = None

@app.get("/")
def home():
    return {"message": "Nexora.ai - A.AI.P.F.D.S backend is running."}

@app.post("/predict")
def predict(transaction: Transaction):
    if model is None:
        raise HTTPException(status_code=500, detail="Model could not be loaded.")

    try:
        features = [[
            transaction.V1, transaction.V2, transaction.V3, transaction.V4, transaction.V5,
            transaction.V6, transaction.V7, transaction.V8, transaction.V9, transaction.V10,
            transaction.V11, transaction.V12, transaction.V13, transaction.V14, transaction.V15,
            transaction.V16, transaction.V17, transaction.V18, transaction.V19, transaction.V20,
            transaction.V21, transaction.V22, transaction.V23, transaction.V24, transaction.V25,
            transaction.V26, transaction.V27, transaction.V28, transaction.Amount
        ]]
        prediction = model.predict(features)[0]
        label = "Fraudulent Transaction" if prediction == 1 else "Legitimate Transaction"
        return {"prediction": int(prediction), "message": label}

    except Exception as e:
        print("❌ Prediction Error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error during prediction. Check logs.")


