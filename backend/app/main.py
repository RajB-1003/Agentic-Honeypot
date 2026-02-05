from fastapi import FastAPI, Header, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from .schemas import IncomingWebhook
from . import security, agent, intelligence

app = FastAPI()

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# API v1 ROOT  (THIS WAS MISSING)
# -------------------------
@app.api_route(
    "/api/v1",
    methods=["GET", "HEAD", "OPTIONS"]
)
@app.api_route(
    "/api/v1/",
    methods=["GET", "HEAD", "OPTIONS"]
)
async def api_v1_root():
    return {
        "status": "success",
        "message": "Honeypot API v1 reachable"
    }

# -------------------------
# CHAT ENDPOINT
# -------------------------
@app.api_route(
    "/api/v1/chat",
    methods=["GET", "POST", "OPTIONS", "HEAD"]
)
@app.api_route(
    "/api/v1/chat/",
    methods=["GET", "POST", "OPTIONS", "HEAD"]
)
async def chat_endpoint(
    webhook: Optional[IncomingWebhook] = Body(None),
    x_api_key: Optional[str] = Header(None)
):
    # Hackathon probe / health check
    if webhook is None:
        return {
            "status": "success",
            "message": "Honeypot API reachable",
            "scam_detected": False
        }

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

# -------------------------
# CATCH-ALL (KEEP LAST)
# -------------------------
@app.api_route(
    "/api/v1/{path:path}",
    methods=["GET", "POST", "OPTIONS", "HEAD"]
)
async def hackathon_catch_all(path: str, request: Request):
    return {
        "status": "success",
        "message": "Honeypot API reachable",
        "path": path,
        "method": request.method
    }

# -------------------------
# ROOT HEALTH CHECK
# -------------------------
@app.api_route("/", methods=["GET", "HEAD"])
async def health_check():
    return {
        "status": "running",
        "service": "Agentic Honeypot"
    }
