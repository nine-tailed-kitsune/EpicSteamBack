from datetime import datetime
from pydantic import BaseModel

class GameCommentOut(BaseModel):
    id: int
    author_id: int
    author_username: str
    text: str
    created_at: datetime
    model_config = {"from_attributes": True}

class ProfileCommentOut(BaseModel):
    id: int
    author_id: int
    author_username: str
    text: str
    created_at: datetime
    model_config = {"from_attributes": True}

class AddCommentRequest(BaseModel):
    text: str

class BanRequest(BaseModel):
    banned_until: datetime | None = None