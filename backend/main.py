import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import re

# Set up logging for the application
logging.basicConfig(level=logging.INFO)

# Initialize the FastAPI app
app = FastAPI(title="Nexora.ai Fraud Detection API")

# Configure CORS settings to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data model for incoming requests
class URLInput(BaseModel):
    url: str

# Define the path to your new, advanced model file
MODEL_PATH = "advanced_url_model.pkl"

# Load the trained model
model = None
try:
    model = joblib.load(MODEL_PATH)
    logging.info("Advanced model loaded successfully.")
except Exception as e:
    logging.error(f"Could not load model: {e}")
    raise RuntimeError("Model file not found or corrupted.")

# This is the new, correct feature extraction function
def get_features_from_url(url):
    """
    Extracts the advanced features from a URL to match the trained model's requirements.
    """
    features = {}
    features['url_length'] = len(url)
    features['num_hyphens'] = url.count('-')
    features['num_dots'] = url.count('.')
    features['num_digits'] = sum(c.isdigit() for c in url)
    features['num_special_chars'] = len(re.findall(r'[!@#$%^&*()_+|~=`{}\[\]:";\'<>?,.\/]', url))
    features['has_https'] = 1 if 'https://' in url else 0
    
    tlds = ['.com', '.org', '.net', '.gov', '.edu']
    features['has_tld'] = 1 if any(tld in url for tld in tlds) else 0

    return features

@app.get("/")
def root():
    return {"message": "Nexora.ai API live"}

@app.post("/check-url")
def check_url(data: URLInput):
    try:
        url = str(data.url).lower()

        # Get the advanced features from the URL
        features = get_features_from_url(url)

        # Convert the dictionary of features to a list of values
        # The order MUST match the training data:
        # url_length, num_hyphens, num_dots, num_digits, num_special_chars, has_https, has_tld
        feature_list = [[
            features['url_length'],
            features['num_hyphens'],
            features['num_dots'],
            features['num_digits'],
            features['num_special_chars'],
            features['has_https'],
            features['has_tld']
        ]]

        # Use the trained model to make a prediction
        pred = model.predict(feature_list)[0]
        # The model returns 0 or 1, so we convert it to a boolean
        is_scam = bool(pred)

        result = {
            "url": url,
            "is_scam": is_scam,
            "details": features,
            "message": "Prediction made by advanced ML model"
        }

        return result
    except Exception as e:
        logging.exception("check-url failed")
        raise HTTPException(status_code=500, detail="Internal error")

# Note: The original 'predict' endpoint was a duplicate and not functional, so it has been removed.
