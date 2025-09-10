import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import ipaddress
import time

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Nexora.ai Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLInput(BaseModel):
    url: str

# This is the new, working model file you created
MODEL_PATH = "fraud_model.pkl"
model = None
try:
    model = joblib.load(MODEL_PATH)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Could not load model: {e}")
    raise RuntimeError("Model file not found or corrupted.")

@app.get("/")
def root():
    return {"message": "Nexora.ai API live"}

def get_features_from_url(url):
    """
    Extracts a number of features from a given URL to match the Kaggle dataset.
    Note: Most of these are placeholders as a real transaction would have them.
    """
    
    # Placeholder values for demonstration
    # In a real app, these would come from the transaction data, not the URL.
    features = {
        # Feature from the URL
        "Time": time.time(),
        
        # 28 PCA components (placeholders)
        "V1": -1.3598, "V2": -0.0728, "V3": 2.5363, "V4": 1.3781,
        "V5": -0.3383, "V6": 0.4623, "V7": 0.2396, "V8": 0.0986,
        "V9": 0.3637, "V10": 0.0907, "V11": -0.5516, "V12": -0.6178,
        "V13": -0.9913, "V14": -0.3111, "V15": 1.4681, "V16": -0.4704,
        "V17": 0.2079, "V18": 0.0257, "V19": 0.4039, "V20": 0.2514,
        "V21": -0.0183, "V22": 0.2778, "V23": -0.1105, "V24": 0.0669,
        "V25": 0.1285, "V26": -0.1891, "V27": 0.1336, "V28": -0.0210,

        # Final feature
        "Amount": 149.62
    }
    
    return features

@app.post("/check-url")
def check_url(data: URLInput):
    try:
        url = str(data.url).lower()
        
        # Get the features from the URL
        features = get_features_from_url(url)
        
        # Convert features to a list in the correct order for the model
        feature_list = [[
            features['Time'], features['V1'], features['V2'], features['V3'], features['V4'],
            features['V5'], features['V6'], features['V7'], features['V8'], features['V9'],
            features['V10'], features['V11'], features['V12'], features['V13'], features['V14'],
            features['V15'], features['V16'], features['V17'], features['V18'], features['V19'],
            features['V20'], features['V21'], features['V22'], features['V23'], features['V24'],
            features['V25'], features['V26'], features['V27'], features['V28'], features['Amount']
        ]]
        
        # Use the trained model to make a prediction
        pred = model.predict(feature_list)[0]
        is_scam = bool(pred)
        
        result = {
            "url": url,
            "is_scam": is_scam,
            "details": features,
            "message": "Prediction made by ML model"
        }
        
        return result
    except Exception as e:
        logging.exception("check-url failed")
        raise HTTPException(status_code=500, detail="Internal error")

# Note: The predict endpoint is not functional in this final version,
# as it's not being used by the front end.
