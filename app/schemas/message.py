from datetime import datetime
from pydantic import BaseModel

class SendMessageRequest(BaseModel):
    text: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    sender_username: str
    receiver_id: int
    receiver_username: str
    text: str
    is_read: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class ConversationOut(BaseModel):
    user_id: int
    username: str
    avatar_url: str | None
    last_message: str
    last_message_at: datetime
    unread_count: int
