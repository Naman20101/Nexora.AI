from difflib import SequenceMatcher

trusted_brands = ["google", "amazon", "paypal", "apple", "samsung", "facebook", "instagram"]

def detect_typosquatting(domain: str) -> bool:
    domain = domain.lower().split('.')[0]
    for brand in trusted_brands:
        similarity = SequenceMatcher(None, domain, brand).ratio()
        if 0.75 < similarity < 1.0:  # not exact match but suspiciously close
            return True
    return False
