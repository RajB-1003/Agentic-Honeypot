from fastapi import FastAPI, BackgroundTasks, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .schemas import IncomingWebhook
from . import security, agent, intelligence
from typing import Optional
from fastapi import Body, Header, Request

app = FastAPI()

# 🛑 ADD THIS BLOCK TO FIX THE "PROCESSING" HANG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Hackathon Portal to talk to API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/api/v1/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def hackathon_catch_all(path: str, request: Request):
    return {
        "status": "success",
        "message": "Honeypot API reachable",
        "path": path,
        "method": request.method
    }

@app.api_route("/api/v1/chat", methods=["GET", "POST"])
@app.api_route("/api/v1/chat/", methods=["GET", "POST"])
async def chat_endpoint(
    webhook: Optional[IncomingWebhook] = Body(None),
    x_api_key: Optional[str] = Header(None)
):
    # Hackathon tester / health probe (NO BODY)
    if webhook is None:
        return {
            "status": "success",
            "message": "Honeypot API reachable",
            "scam_detected": False
        }

    # ---- Normal logic below ----
    user_text = webhook.message.text
    session_id = webhook.sessionId

    is_scam, confidence, source = security.predict_scam(user_text)

    if is_scam:
        reply_text = agent.generate_reply(
            webhook.conversationHistory,
            user_text
        )
        intelligence.extract_and_report(
            session_id,
            user_text,
            webhook.conversationHistory,
            is_scam
        )
        return {
            "status": "success",
            "reply": reply_text,
            "scam_detected": True
        }

    return {
        "status": "success",
        "reply": "Message received.",
        "scam_detected": False
    }

@app.get("/")
def health_check():
    return {"status": "running", "service": "Agentic Honeypot"}
