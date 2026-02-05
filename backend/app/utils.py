import re
from urllib.parse import urlparse

def get_domain(url: str) -> str:
    """Extracts root domain from URL."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        parsed = urlparse(url)
        return parsed.netloc.split(':')[0]
    except:
        return ""

def extract_intelligence(text: str) -> dict:
    """
    Extracts all required fields for the GUVI Evaluation.
    """
    intelligence = {
        "phishingLinks": [],  # Renamed from 'urls' to match spec
        "emails": [],
        "phoneNumbers": [],   # Renamed from 'phone_numbers'
        "bankAccounts": [],   # NEW
        "upiIds": [],
        "suspiciousKeywords": [] # NEW
    }

    # 1. Phishing Links (URLs)
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w%./?&;=+]*)?'
    intelligence["phishingLinks"] = list(set(re.findall(url_pattern, text)))

    # 2. Emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    intelligence["emails"] = list(set(re.findall(email_pattern, text)))

    # 3. Phone Numbers
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    intelligence["phoneNumbers"] = list(set([p for p in phones if len(re.sub(r'\D', '', p)) >= 10]))

    # 4. Bank Account Numbers (Generic 9-18 digits)
    bank_pattern = r'\b\d{9,18}\b'
    # Filter out phone numbers from this list (basic heuristic)
    potential_banks = re.findall(bank_pattern, text)
    intelligence["bankAccounts"] = [b for b in potential_banks if b not in intelligence["phoneNumbers"]]

    # 5. UPI IDs
    upi_pattern = r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}'
    upis = re.findall(upi_pattern, text)
    intelligence["upiIds"] = list(set([u for u in upis if u not in intelligence["emails"]]))

    # 6. Suspicious Keywords (Simple dictionary check)
    triggers = ["urgent", "verify", "block", "suspend", "kyc", "lapse", "immediately", "refund", "winner", "lottery"]
    found_keywords = [word for word in triggers if word in text.lower()]
    intelligence["suspiciousKeywords"] = list(set(found_keywords))

    return intelligence