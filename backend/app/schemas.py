from typing import List, Optional
from pydantic import BaseModel

class MessageDetail(BaseModel):
    sender: str
    text: str
    timestamp: int

class IncomingWebhook(BaseModel):
    sessionId: str
    message: MessageDetail
    conversationHistory: List[MessageDetail]
    metadata: Optional[dict] = None
