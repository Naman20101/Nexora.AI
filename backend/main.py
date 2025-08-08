from url_checks import detect_typosquatting
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
import joblib
import uvicorn
import requests
from bs4 import BeautifulSoup
import tldextract
import whois
from datetime import datetime
from urllib.parse import urlparse

app = FastAPI(
    title="Nexora.ai Fraud Detection API",
    description="Detects fraud via transaction data or suspicious URLs",
    version="2.0.0"
)

# Load your ML model
model = joblib.load("fraud_model.pkl")

# ----------- MODELS -----------
class PredictionInput(BaseModel):
    feature1: float
    feature2: float
    # Add other features here...

class URLInput(BaseModel):
    url: HttpUrl

# ----------- ROUTES -----------

@app.get("/")
def read_root():
    return {"message": "Welcome to Nexora.ai Fraud Detection API"}

@app.post("/predict")
def predict(data: PredictionInput):
    features = [[data.feature1, data.feature2]]
    prediction = model.predict(features)[0]
    return {"fraud_prediction": int(prediction)}

@app.post("/check-url")
def check_url(data: URLInput):
    url = str(data.url)

    # Step 1: Keyword detection
    suspicious_keywords = [
        "login", "verify", "account", "secure", "update", "banking",
        "paypal-security", "free-gift", "prize", "win", "alert"
    ]
    keyword_flag = any(word in url.lower() for word in suspicious_keywords)

    # Step 2: Domain info
    domain_info = tldextract.extract(url)
    domain_name = f"{domain_info.domain}.{domain_info.suffix}"

    try:
        w = whois.whois(domain_name)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        domain_age_days = (datetime.now() - creation_date).days if creation_date else None
    except Exception:
        domain_age_days = None

    domain_age_flag = domain_age_days is not None and domain_age_days < 180

    # Step 3: HTML content scan
    html_flag = False
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find_all("input", {"type": "password"}) or soup.find_all("iframe"):
            html_flag = True
    except Exception:
        html_flag = False

    # Step 4: Advanced AI-like checks from url_checks
    from url_checks import detect_typosquatting, detect_homograph, uses_ip_address, is_shortened_url

    typosquatting_flag = detect_typosquatting(url)
    homograph_flag = detect_homograph(url)
    ip_flag = uses_ip_address(url)
    shortened_flag = is_shortened_url(url)

    # Final decision
    is_scam = any([
        keyword_flag, domain_age_flag, html_flag,
        typosquatting_flag, homograph_flag, ip_flag, shortened_flag
    ])

    return {
        "url": url,
        "is_scam": is_scam,
        "flags_triggered": {
            "keyword_flag": keyword_flag,
            "domain_age_days": domain_age_days,
            "domain_age_flag": domain_age_flag,
            "html_flag": html_flag,
            "typosquatting_flag": typosquatting_flag,
            "homograph_flag": homograph_flag,
            "ip_flag": ip_flag,
            "shortened_url_flag": shortened_flag
        },
        "message": "⚠️ This link may be fraudulent!" if is_scam else "✅ URL seems safe."
    }