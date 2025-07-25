from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI()

class InputData(BaseModel):
    features: list  # expects a list of numbers

try:
    with open("fraud_model (2).pkl", "rb") as f:
        model = pickle.load(f)
    model_ready = True
except Exception as e:
    model_ready = False
    model = None
    print(f"Model loading failed: {e}")

@app.get("/")
def root():
    return {"status": "Model is ready" if model_ready else "Model failed to load"}

@app.post("/predict")
def predict(data: InputData):
    if not model_ready:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        features = np.array(data.features).reshape(1, -1)
        prediction = model.predict(features)
        return {"prediction": prediction.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


