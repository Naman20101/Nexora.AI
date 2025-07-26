from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import joblib
import os

# App metadata and Swagger UI description
app = FastAPI(
    title="🔍 Nexora.ai — Advanced Fraud Detection API ",
    description="""
💳 **Advanced Real-Time Credit Card Fraud Detection API**

🧠 **Model Type**: Supervised Machine Learning  
📚 **Dataset**: [Kaggle’s Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)  
📊 **Transactions**: 284,807 total — only 492 fraud cases  
⚙️ **Stack**: FastAPI · scikit-learn · joblib · Render/Vercel · React Frontend  
🔐 **Security**: Input validation (Pydantic) · Pickle-safe loading  

---

### 📌 Endpoints:
- `GET /` → Health check (returns app status)
- `POST /predict` → Fraud prediction from 30 V1–V28, Time & Amount features

👨‍💻 **Developed by**: Naman Reddy  
🔒 **Status**: Alpha v1.0 (Private Test Deployment)

""",
    version="1.0.0"
)

# Path to model
MODEL_PATH = "fraud_model.pkl"

# Load model
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
else:
    print("❌ Model not found - waiting for upload")


# Pydantic input schema
class FraudInput(BaseModel):
    features: List[float]  # Length must be 30


# Root health check
@app.get("/")
def read_root():
    if model is None:
        return {"status": "Model not ready. Please upload model file."}
    return {"status": "Nexora.ai API is live 🚀", "model": "Loaded ✅"}


# Prediction endpoint
@app.post("/predict")
def predict_fraud(data: FraudInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    if len(data.features) != 30:
        raise HTTPException(status_code=422, detail="Exactly 30 features required")

    try:
        prediction = model.predict([data.features])[0]
        return {
            "prediction": int(prediction),
            "result": "Fraudulent" if prediction == 1 else "Legitimate"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")



