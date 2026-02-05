from fastapi import FastAPI, Header, Body
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
# API v1 ROOT (EXPLICIT)
# -------------------------
@app.get("/api/v1")
@app.head("/api/v1")
@app.options("/api/v1")
async def api_v1_root():
    return {
        "status": "success",
        "message": "Honeypot API v1 reachable"
    }

@app.get("/api/v1/")
@app.head("/api/v1/")
@app.options("/api/v1/")
async def api_v1_root_slash():
    return {
        "status": "success",
        "message": "Honeypot API v1 reachable"
    }

# -------------------------
# CHAT ENDPOINT
# -------------------------
@app.post("/api/v1/chat")
@app.get("/api/v1/chat")
@app.head("/api/v1/chat")
@app.options("/api/v1/chat")
async def chat_endpoint(
    webhook: Optional[IncomingWebhook] = Body(None),
    x_api_key: Optional[str] = Header(None)
):
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

@app.post("/api/v1/chat/")
@app.get("/api/v1/chat/")
@app.head("/api/v1/chat/")
@app.options("/api/v1/chat/")
async def chat_endpoint_slash(
    webhook: Optional[IncomingWebhook] = Body(None),
    x_api_key: Optional[str] = Header(None)
):
    return await chat_endpoint(webhook, x_api_key)

# -------------------------
# ROOT HEALTH CHECK
# -------------------------
@app.get("/")
@app.head("/")
async def health_check():
    return {
        "status": "running",
        "service": "Agentic Honeypot"
    }
