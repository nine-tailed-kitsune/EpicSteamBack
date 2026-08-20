from datetime import datetime
from pydantic import BaseModel

class FriendRequestOut(BaseModel):
    id: int
    sender_id: int
    sender_username: str
    receiver_id: int
    receiver_username: str
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}

class FriendOut(BaseModel):
    id: int
    username: str
    avatar_url: str | None
    model_config = {"from_attributes": True}
