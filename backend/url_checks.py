import re
import socket
import tldextract

def detect_typosquatting(url):
    # Compare domain against known trusted domains
    trusted_domains = [
        "paypal.com", "google.com", "amazon.com", "apple.com", "facebook.com", 
        "instagram.com", "microsoft.com", "bankofamerica.com", "wellsfargo.com"
    ]
    extracted = tldextract.extract(url)
    current_domain = f"{extracted.domain}.{extracted.suffix}"

    for trusted in trusted_domains:
        if levenshtein(current_domain, trusted) <= 2 and current_domain != trusted:
            return True
    return False

def detect_homograph(url):
    try:
        url.encode('ascii')  # If it can't be encoded in ASCII, it's suspicious
        return False
    except UnicodeEncodeError:
        return True

def uses_ip_address(url):
    match = re.match(r'https?://(\d{1,3}\.){3}\d{1,3}', url)
    return bool(match)

def is_shortened_url(url):
    known_shorteners = [
        "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "buff.ly", "is.gd", "cutt.ly"
    ]
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    return domain in known_shorteners

# Helper function for typosquatting
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 
            deletions = current_row[j] + 1       
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]