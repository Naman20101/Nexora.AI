from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os

# Load the model once when the server starts
model_path = "fraud_model.pkl"
if not os.path.exists(model_path):
    raise FileNotFoundError("Model file not found!")

model = joblib.load("fraud_model.pkl")

# Define the FastAPI app
app = FastAPI()

# Define input format
class FraudInput(BaseModel):
    features: list  # list of numerical values

@app.get("/")
def read_root():
    return {"message": "Fraud Detection API is running"}

@app.post("/predict")
def predict(input: FraudInput):
    try:
        input_data = np.array(input.features).reshape(1, -1)
        prediction = model.predict(input_data)[0]
        return {"prediction": int(prediction)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


