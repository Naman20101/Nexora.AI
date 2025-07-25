from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

app = FastAPI(title="Nexora.AI – A.Al.F.D.S")

model = joblib.load("fraud_model.pkl")  # We'll link the hosted model later

class Transaction(BaseModel):
    feature1: float
    feature2: float
    feature3: float
    feature4: float
    # Extend with real features

@app.post("/predict")
def predict(transaction: Transaction):
    features = np.array([[transaction.feature1, transaction.feature2, transaction.feature3, transaction.feature4]])
    prediction = model.predict(features)
    return {"fraudulent": bool(prediction[0])}
