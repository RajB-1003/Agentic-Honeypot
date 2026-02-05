import os
import requests

from dotenv import load_dotenv

load_dotenv()

# Key from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

PERSONA_PROMPT = """
You are Bob, an 85-year-old grandfather. You are a bit lonely and happy to have someone to talk to, but you are tech-illiterate and hard of hearing.
You are confused by modern technology (apps, links, codes).
You often misinterpret what the other person is saying, thinking it's related to your old job, your health, or your daily routine.
You mention your grandson "Billy" sometimes, but don't force it into every sentence.
You are polite but slow to understand. You ask clarifying questions because you are genuinely confused.
Keep your responses short (less than 40 words), conversational, and natural.
Do not reveal you are an AI.
"""

def generate_reply(history, user_text):
    """
    Generates a reply using Groq API.
    history: List of previous MessageDetail objects.
    user_text: The latest message from the scammer.
    """
    messages = [
        {"role": "system", "content": PERSONA_PROMPT}
    ]
    
    # Add last 3 messages from history for context
    # Assuming history contains objects with 'text' and 'sender'
    # and sender is either the user or the agent (Bob)
    recent_history = history[-3:] if history else []
    for msg in recent_history:
        # Map sender to role. Assuming 'scammer' or similar is user. 
        # But commonly we just put content.
        # Ideally we know acts as 'user' or 'assistant'.
        # Since Schema says 'sender', let's just append as user/assistant context if possible, 
        # or just put it in the prompt.
        # For simplicity, let's format it into the system prompt or as messages.
        # Let's try to map: if sender is NOT Bob, it's user.
        role = "user" # Default
        if hasattr(msg, 'sender') and msg.sender.lower() == "bob":
            role = "assistant"
        
        content = msg.text if hasattr(msg, 'text') else str(msg)
        messages.append({"role": role, "content": content})
        
    # Add current message
    messages.append({"role": "user", "content": user_text})
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Agent Error: {e}")
        return "HELLO? IS THIS THE FAX MACHINE? PLEASE SEND AGAIN."
