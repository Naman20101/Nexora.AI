import os
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

load_dotenv()

router = APIRouter()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


class SafeURLInput(BaseModel):
    url: str


@router.post("/check-url")
def safe_check_url(data: SafeURLInput):
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="Google Safe Browsing API key not configured.")

    url = data.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    safe_browsing_endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

    payload = {
        "client": {
            "clientId": "nexora-ai",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(
            f"{safe_browsing_endpoint}?key={GOOGLE_API_KEY}",
            json=payload,
            timeout=5
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Safe Browsing API request failed: {str(e)}")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Google Safe Browsing API returned an error.")

    result = response.json()

    if result.get("matches"):
        threat_types = list({m.get("threatType", "UNKNOWN") for m in result["matches"]})
        return {
            "url": url,
            "is_safe": False,
            "threats": threat_types,
            "message": f"THREAT: Google flagged this URL — {', '.join(threat_types)}"
        }

    return {"url": url, "is_safe": True, "message": "Google Safe Browsing: No threats detected."}
