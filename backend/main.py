from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# Load model
model = joblib.load("fraud_model.pkl")

# Define input structure
class Transaction(BaseModel):
    feature1: float
    feature2: float
    feature3: float
    feature4: float
    feature5: float
    feature6: float
    feature7: float
    feature8: float
    feature9: float
    feature10: float
    feature11: float
    feature12: float
    feature13: float
    feature14: float
    feature15: float
    feature16: float
    feature17: float
    feature18: float
    feature19: float
    feature20: float
    feature21: float
    feature22: float
    feature23: float
    feature24: float
    feature25: float
    feature26: float
    feature27: float
    feature28: float
    amount: float

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "✅ Nexora.ai Fraud Detection API is live!"}

@app.post("/predict")
def predict_fraud(transaction: Transaction):
    data = np.array([[value for value in transaction.dict().values()]])
    prediction = model.predict(data)[0]
    return {"fraud_prediction": bool(prediction)}

