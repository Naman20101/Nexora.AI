import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import re
import requests
import idna

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Nexora.ai Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is a placeholder for your trained model.
# You would need to train a model on a dataset and save it as this file.
MODEL_PATH = "fraud_model.pkl"
model = None
try:
    model = joblib.load(MODEL_PATH)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.warning(f"Could not load model: {e}")
    model = "placeholder" # Use a placeholder if the model is not found

class URLInput(BaseModel):
    url: str

class SmallPredict(BaseModel):
    feature1: float
    feature2: float
    feature3: float

@app.get("/")
def root():
    return {"message": "Nexora.ai API live"}

@app.post("/check-url")
def check_url(data: URLInput):
    try:
        url = str(data.url).lower()
        
        # Make the URL a proper one if it's missing http:// or https://
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        
        # Initialize flags for the detailed report
        redirect_scam = False
        idn_scam = False
        cert_scam = False
        keyword_scam = False

        # --- Check 1: URL Redirection and HTTPS Certificate ---
        try:
            res = requests.head(url, allow_redirects=True, timeout=5)
            final_url = res.url
            if final_url != url:
                redirect_scam = True
            
            # Check for invalid certificate
            if not final_url.startswith("https://"):
                cert_scam = True
            else:
                requests.get(final_url, timeout=5, verify=True)

        except requests.exceptions.SSLError:
            cert_scam = True
        except requests.exceptions.RequestException:
            pass # Ignore connection errors for this check

        # --- Check 2: Internationalized Domain Names (IDNs) ---
        try:
            domain = url.split("//")[-1].split("/")[0]
            if not domain.isascii():
                ascii_domain = idna.encode(domain).decode('ascii')
                # If the domain has a different ASCII version, it's a homograph attack
                if ascii_domain != domain:
                    idn_scam = True
        except idna.IDNAError:
            idn_scam = True

        # --- Check 3: Simple Keyword and Typos (from previous logic) ---
        suspicious_words = ['verify', 'login', 'account', 'secure', 'update', 'confirm', 'access', 'id', 'password', 'reset', 'sign-in']
        suspicious_tlds = ['.ru', '.cn', '.xyz', '.tk', '.ga', '.ml', '.cf', '.gq', '.pw']
        brand_names = ['paypal', 'google', 'amazon', 'apple', 'microsoft']

        if any(brand in url for brand in brand_names) and any(word in url for word in suspicious_words):
            keyword_scam = True
            
        if any(tld in url for tld in suspicious_tlds):
            keyword_scam = True
        
        if re.search(r'paypa1|amaz0n|goog1e', url):
            keyword_scam = True

        is_scam = redirect_scam or idn_scam or cert_scam or keyword_scam

        result = {
            "url": url, 
            "is_scam": is_scam,
            "details": {
                "redirection_scam": redirect_scam,
                "idn_scam": idn_scam,
                "invalid_cert_scam": cert_scam,
                "keyword_scam": keyword_scam,
            },
            "message": "OK"
        }
        return result
    except Exception as e:
        logging.exception("check-url failed")
        raise HTTPException(status_code=500, detail="Internal error")

@app.post("/predict")
def predict(data: SmallPredict):
    try:
        if model == "placeholder":
            if data.feature1 > 0.8:
                pred = 1
            else:
                pred = 0
        else:
            X = [[data.feature1, data.feature2, data.feature3]]
            pred = int(model.predict(X)[0])
        
        return {"prediction": pred, "result": "Fraud" if pred == 1 else "Legit"}
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("predict failed")
        raise HTTPException(status_code=500, detail=str(e))
