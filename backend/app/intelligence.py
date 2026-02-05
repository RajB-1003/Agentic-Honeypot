import re
import requests
import asyncio
from typing import Dict, Any, List

def extract_intelligence(text: str) -> Dict[str, Any]:
    """
    Extracts structured intelligence from text using Regex.
    """
    intelligence = {
        "phishingLinks": [], 
        "emails": [],
        "phoneNumbers": [], 
        "bankAccounts": [], 
        "upiIds": [],
        "suspiciousKeywords": []
    }

    # 1. Phishing Links (URLs)
    # Matches http/https
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w%./?&;=+]*)?'
    intelligence["phishingLinks"] = list(set(re.findall(url_pattern, text)))

    # 2. Emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    intelligence["emails"] = list(set(re.findall(email_pattern, text)))

    # 3. Phone Numbers (+91 or generic)
    # Matches +91... or 10 digits
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    # Filter for valid length (approx 10+)
    intelligence["phoneNumbers"] = list(set([p for p in phones if len(re.sub(r'\D', '', p)) >= 10]))

    # 4. Bank Account Numbers (9-18 digits)
    bank_pattern = r'\b\d{9,18}\b'
    potential_banks = re.findall(bank_pattern, text)
    # Exclude if it looks like a phone number we already found? 
    # Or just keep it. Conflict resolution simple: if in phones, exclude.
    # But phone pattern might extract bank numbers too.
    # Simple deduplication:
    intelligence["bankAccounts"] = [b for b in potential_banks if b not in intelligence["phoneNumbers"]]

    # 5. UPI IDs (something@upi)
    upi_pattern = r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}'
    upis = re.findall(upi_pattern, text)
    intelligence["upiIds"] = list(set([u for u in upis if u not in intelligence["emails"]]))

    return intelligence

def send_guvi_callback(session_id: str, extracted_data: dict, msg_count: int = 1):
    """
    Sends a fire-and-forget POST request to GUVI hackathon endpoint.
    """
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "extractedIntelligence": extracted_data,
        "messageCount": msg_count, # Optional or derived
        # Spec says: {"sessionId": ..., "scamDetected": true, "extractedIntelligence": {...}, ...}
    }
    
    try:
        # 3-second timeout as requested
        response = requests.post(url, json=payload, timeout=3)
        # We don't really care about the response code for fire-and-forget, but good to log
        # print(f"Callback status: {response.status_code}") 
    except requests.exceptions.Timeout:
        # print("Callback timed out")
        pass
    except Exception as e:
        # print(f"Callback failed: {e}")
        pass

def extract_and_report(session_id: str, text: str, history: List[Any], is_scam: bool) -> Dict[str, Any]:
    """
    Wrapper function to extract intelligence and send report, as expected by main.py.
    """
    # 1. Extract
    extracted_data = extract_intelligence(text)
    
    # 2. Estimate message count
    msg_count = len(history) + 1
    
    # 3. Send Callback (Fire-and-forget)
    # We call it synchronously here as it uses a short timeout, 
    # OR we could rely on BackgroundTasks in main.py, but main.py calls this function 
    # instead of scheduling the callback directly.
    # The snippet implies this function handles the logic.
    # To keep it non-blocking in main's context, main seems to rely on this being fast 
    # OR main should have scheduled THIS function as a background task.
    # Wait, the user's main.py says: 
    # "intelligence.extract_and_report(..., is_scam)" 
    # AND "intelligence.extract_and_report handles the callback logic internally".
    # But main.py calls it *synchronously* inside the endpoint, NOT via background_tasks.add_task.
    # This implies send_guvi_callback's short timeout is relied upon.
    
    send_guvi_callback(session_id, extracted_data, msg_count)
    
    return extracted_data
