import requests
import time

# ✅ YOUR LIVE RENDER URL
LIVE_URL = "https://agentic-honeypot-tj31.onrender.com/api/v1/chat"

print(f"🚀 WAKING UP SERVER: {LIVE_URL}")
print("⏳ This might take 50 seconds if the server is sleeping...")

payload = {
  "sessionId": "test_live_001",
  "message": {
    "sender": "scammer",
    "text": "URGENT: Your bank account is blocked. Verify KYC immediately at http://bit.ly/scam",
    "timestamp": 1770005528999
  },
  "conversationHistory": [],
  "metadata": {"channel": "LiveTest"}
}

try:
    start = time.time()
    # 60s timeout to allow for "Cold Start"
    response = requests.post(LIVE_URL, json=payload, timeout=60)
    latency = (time.time() - start)

    print(f"\n✅ STATUS: {response.status_code}")
    print(f"⏱️ TIME:   {latency:.2f}s")
    
    if response.status_code == 200:
        print(f"🤖 REPLY:  {response.json().get('reply')}")
        print("\n🎉 SUCCESS! Your API is PUBLIC and READY for the Hackathon.")
    else:
        print(f"❌ ERROR: {response.text}")

except Exception as e:
    print(f"\n❌ CONNECTION FAILED: {e}")
    print("👉 Check Render Logs for 'Crash' or 'Memory' errors.")