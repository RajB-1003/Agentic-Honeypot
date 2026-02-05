from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# 1. The Message Model (This was missing)
class Message(BaseModel):
    text: str
    sender: Optional[str] = "user"
    timestamp: Optional[str] = None

# 2. The Request Model
class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: Optional[List[Any]] = []
    metadata: Optional[Dict[str, Any]] = {}

# 3. The Response Model
class APIResponse(BaseModel):
    status: str
    reply: str
    scam_detected: bool
    confidence: float