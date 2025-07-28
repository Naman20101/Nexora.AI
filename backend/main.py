from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import uvicorn

app = FastAPI()

# Load model
model = joblib.load("fraud_model.pkl")

# Define input schema
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

@app.get("/")
def home():
    return {"message": "Nexora.ai - A.P.F.D.S backend is running."}

@app.post("/predict")
def predict(transaction: Transaction):
    data = np.array([[getattr(transaction, f"V{i}") for i in range(1, 29)] + [transaction.Amount]])
    prediction = model.predict(data)[0]
    return {
        "prediction": int(prediction),
        "message": "Fraudulent Transaction" if prediction == 1 else "Legitimate Transaction"
    }

# Uncomment this if you're testing locally:
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


