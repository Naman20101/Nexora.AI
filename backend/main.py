from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Model is ready"}

@app.post("/predict")
def predict(data: dict):
    model = joblib.load("fraud_model.pkl")
    features = np.array([list(data.values())])
    prediction = model.predict(features)
    return {"prediction": prediction.tolist()}

