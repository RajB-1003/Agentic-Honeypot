from fastapi import FastAPI, BackgroundTasks, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .schemas import IncomingWebhook
from . import security, agent, intelligence

app = FastAPI()

# 🛑 ADD THIS BLOCK TO FIX THE "PROCESSING" HANG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Hackathon Portal to talk to API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/chat")
async def chat_endpoint(
    webhook: Optional[IncomingWebhook] = None,
    background_tasks: BackgroundTasks = None,
    x_api_key: Optional[str] = Header(None)
):
    """
    Main chat endpoint for the Honeypot.
    """
    if webhook is None:
        return {
            "status": "success",
            "message": "Honeypot API reachable",
            "scam_detected": False
        }

    try:
        user_text = webhook.message.text
        session_id = webhook.sessionId
        
        # 1. Security Check (Scam Detection)
        # Returns: is_scam, confidence, source (Model/Keyword)
        is_scam, confidence, source = security.predict_scam(user_text)
        
        if is_scam:
            # 2. Generate Agent Reply (Persona "Bob")
            # Pass conversation history
            reply_text = agent.generate_reply(webhook.conversationHistory, user_text)
            
            # 3. Extract Intelligence and Send Callback
            # This function handles extraction and the GUVI callback internally
            extracted_data = intelligence.extract_and_report(session_id, user_text, webhook.conversationHistory, is_scam)
            
            return {
                "status": "success",
                "reply": reply_text,
                "scam_detected": True
            }
        else:
            # Safe Message
            return {
                "status": "success",
                "reply": "Message received.",
                "scam_detected": False
            }
            
    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        # Return a valid JSON even on error so the portal doesn't hang
        return {
            "status": "error",
            "reply": "System maintenance. Please try again later."
        }

@app.get("/")
def health_check():
    return {"status": "running", "service": "Agentic Honeypot"}
