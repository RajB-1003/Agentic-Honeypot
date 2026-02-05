import requests
import time
import sys

# ✅ Point to your Render URL or Localhost
# BACKEND_URL = "https://honeypot-defense-system.onrender.com/api/v1/chat"
BACKEND_URL = "http://127.0.0.1:8000/api/v1/chat"

scam_script = [
    "Hi, do you want to earn Rs. 5000 daily working from home?",
    "This is a limited offer for Amazon part-time job.",
    "You just need to like YouTube videos and get paid.",
    "Payment proof attached. Message me now.",
    "Last chance. Positions are filling up."
]

print("-" * 60)
print("🚀 STARTING REAL AI SIMULATION (NO FALLBACKS)")
print(f"📡 Connecting to: {BACKEND_URL}")
print("-" * 60)

session_id = f"sim_{int(time.time())}"
history = []

for i, turn in enumerate(scam_script):
    print(f"\n[TURN {i+1}] Scammer: {turn}")
    
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": turn,
            "timestamp": int(time.time())
        },
        "conversationHistory": history
    }
    
    try:
        # ⏳ WAIT 60 SECONDS (Groq needs time!)
        start = time.time()
        response = requests.post(BACKEND_URL, json=payload, timeout=60)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            # THIS IS THE REAL AI REPLY
            data = response.json()
            reply = data.get("reply", "No reply field")
            print(f"   🤖 Bob (Real): \"{reply}\"")
            print(f"      (Took {latency:.0f}ms)")
            
            # Update History
            history.append({"sender": "scammer", "text": turn, "timestamp": int(time.time())})
            history.append({"sender": "agent", "text": reply, "timestamp": int(time.time())})
        else:
            print(f"   ❌ SERVER ERROR: {response.status_code}")
            print(f"   ⚠️ Raw: {response.text}")
            
    except Exception as e:
        print(f"   ❌ CONNECTION DIED: {e}")
        print("   (Check if your uvicorn server is running!)")
        break

    time.sleep(1) # Breathe