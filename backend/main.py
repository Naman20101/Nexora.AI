from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import numpy as np
import os

app = FastAPI(
    title="Nexora.ai - Advanced AI-Powered Fraud Detection System (A.AI.P.F.D.S)",
    description="""
An advanced fraud detection API trained on Kaggle's 284,807 transaction dataset.

🚀 Features:
- Uses high-dimensional PCA components (V1–V28), amount, and time
- Capable of real-time fraud classification
- Designed for integration with UPI apps (Paytm, PhonePe, GPay, etc.)
- Ready for LLM integration & scalable cloud deployment

🔧 Built by **Naman Reddy** for academic & university-level applications.
""",
    version="1.0.0"
)

# Input model
class TransactionData(BaseModel):
    time: float = Field(..., description="Time since the first transaction in the dataset", example=100000.0)
    v1: float = Field(..., description="PCA feature V1", example=-1.359807)
    v2: float = Field(..., description="PCA feature V2", example=-0.072781)
    v3: float = Field(..., description="PCA feature V3", example=2.536346)
    v4: float = Field(..., description="PCA feature V4", example=1.378155)
    v5: float = Field(..., description="PCA feature V5", example=-0.338321)
    v6: float = Field(..., description="PCA feature V6", example=0.462388)
    v7: float = Field(..., description="PCA feature V7", example=0.239599)
    v8: float = Field(..., description="PCA feature V8", example=0.098698)
    v9: float = Field(..., description="PCA feature V9", example=0.363787)
    v10: float = Field(..., description="PCA feature V10", example=0.090794)
    v11: float = Field(..., description="PCA feature V11", example=-0.5516)
    v12: float = Field(..., description="PCA feature V12", example=-0.6178)
    v13: float = Field(..., description="PCA feature V13", example=-0.99139)
    v14: float = Field(..., description="PCA feature V14", example=-0.311169)
    v15: float = Field(..., description="PCA feature V15", example=1.468177)
    v16: float = Field(..., description="PCA feature V16", example=-0.470401)
    v17: float = Field(..., description="PCA feature V17", example=0.207971)
    v18: float = Field(..., description="PCA feature V18", example=0.025791)
    v19: float = Field(..., description="PCA feature V19", example=0.403993)
    v20: float = Field(..., description="PCA feature V20", example=0.251412)
    v21: float = Field(..., description="PCA feature V21", example=-0.018307)
    v22: float = Field(..., description="PCA feature V22", example=0.277838)
    v23: float = Field(..., description="PCA feature V23", example=-0.110474)
    v24: float = Field(..., description="PCA feature V24", example=-0.168486)
    v25: float = Field(..., description="PCA feature V25", example=0.270830)
    v26: float = Field(..., description="PCA feature V26", example=0.018343)
    v27: float = Field(..., description="PCA feature V27", example=0.277837)
    v28: float = Field(..., description="PCA feature V28", example=-0.110473)
    amount: float = Field(..., description="Transaction amount", example=149.62)

# Model path
MODEL_PATH = "fraud_model.pkl"

@app.post("/predict")
def predict(transaction: TransactionData):
    if not os.path.exists(MODEL_PATH):
        return {"error": "Model not found. Please train the model and upload 'fraud_model.pkl'."}
    
    model = joblib.load(MODEL_PATH)

    data = np.array([[
        transaction.time, transaction.v1, transaction.v2, transaction.v3, transaction.v4,
        transaction.v5, transaction.v6, transaction.v7, transaction.v8, transaction.v9,
        transaction.v10, transaction.v11, transaction.v12, transaction.v13, transaction.v14,
        transaction.v15, transaction.v16, transaction.v17, transaction.v18, transaction.v19,
        transaction.v20, transaction.v21, transaction.v22, transaction.v23, transaction.v24,
        transaction.v25, transaction.v26, transaction.v27, transaction.v28, transaction.amount
    ]])

    prediction = model.predict(data)[0]
    return {
        "prediction": int(prediction),
        "result": "Fraud" if prediction == 1 else "Legitimate"
    }

