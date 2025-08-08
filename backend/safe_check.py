# safe_check.py

import requests
from fastapi import APIRouter, HTTPException, Body

router = APIRouter()

API_KEY = "YOUR_GOOGLE_SAFE_BROWSING_API_KEY"  # Replace with your real key

@router.post("/check-url")
def check_url(url: str = Body(...)):
    safe_browsing_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    
    payload = {
        "client": {
            "clientId": "nexora-ai",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    response = requests.post(
        f"{safe_browsing_url}?key={API_KEY}",
        json=payload
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Google Safe Browsing API error.")

    result = response.json()
    if result.get("matches"):
        return {"status": "unsafe", "details": result["matches"]}
    else:
        return {"status": "safe"}
