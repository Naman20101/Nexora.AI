from fastapi import FastAPI
import joblib
import numpy as np
from pydantic import BaseModel

app = FastAPI()

class Transaction(BaseModel):
    data: list  # expects 30 features from the creditcard dataset

# Try loading model at startup
try:
    model = joblib.load("fraud_model.pkl")
    print("✅ Model loaded successfully")
except Exception as e:
    model = None
    print(f"❌ Model loading failed: {e}")

@app.get("/")
def read_root():
    return {"message": "Fraud Detection API is running."}

@app.post("/predict")
def predict(transaction: Transaction):
    if model is None:
        return {"status": "Model not loaded"}
    try:
        input_array = np.array(transaction.data).reshape(1, -1)
        prediction = model.predict(input_array)[0]
        return {"prediction": int(prediction)}
    except Exception as e:
        return {"error": str(e)}



