from fastapi import FastAPI, BackgroundTasks, HTTPException
from .schemas import IncomingWebhook
from . import security, agent, intelligence

app = FastAPI()

@app.post("/api/v1/chat")
async def chat_endpoint(webhook: IncomingWebhook, background_tasks: BackgroundTasks):
    """
    Main chat endpoint for the Honeypot.
    """
    try:
        user_text = webhook.message.text
        session_id = webhook.sessionId
        
        # 1. Security Check (Scam Detection)
        is_scam, confidence = security.predict_scam(user_text)
        
        if is_scam:
            # 2. Generate Agent Reply (Persona "Bob")
            # Pass conversation history
            reply_text = agent.generate_reply(webhook.conversationHistory, user_text)
            
            # 3. Extract Intelligence and Send Callback (Background Task)
            extracted_data = intelligence.extract_intelligence(user_text)
            
            # We assume msg_count is length of history + 1. 
            # Or just pass 1 if tracking per message. 
            # The prompt implies aggregations, but 'msg_count' isn't fully defined in schema 
            # so we'll estimate or just pass a value.
            msg_count = len(webhook.conversationHistory) + 1
            
            background_tasks.add_task(
                intelligence.send_guvi_callback, 
                session_id, 
                extracted_data, 
                msg_count
            )
            
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
        # Log error
        print(f"Error in chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
def health_check():
    return {"status": "running", "service": "Agentic Honeypot"}
