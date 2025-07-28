from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pickle

app = FastAPI()

# Load model
with open("fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

class Transaction(BaseModel):
    features: list  # expects a list of 30 float values

@app.get("/")
def root():
    return {"message": "✅ Fraud Detection API is running!"}

@app.post("/predict")
def predict(transaction: Transaction):
    try:
        input_data = np.array(transaction.features).reshape(1, -1)
        prediction = model.predict(input_data)[0]
        result = "Fraudulent" if prediction == 1 else "Legitimate"
        return {"prediction": int(prediction), "result": result}
    except Exception as e:
        return {"error": str(e)}


