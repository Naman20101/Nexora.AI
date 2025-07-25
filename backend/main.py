from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

# Load the trained model
model = joblib.load("fraudmodel.pkl")

# Define the request structure
class TransactionData(BaseModel):
    features: list  # list of numerical values used by the model

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Nexora.AI Fraud Detection API is running."}

@app.post("/predict")
def predict(data: TransactionData):
    try:
        input_array = np.array(data.features).reshape(1, -1)
        prediction = model.predict(input_array)[0]
        return {"fraud": bool(prediction)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

