from datetime import datetime
from pydantic import BaseModel

class ForumPostOut(BaseModel):
    id: int
    author_id: int
    author_username: str
    text: str
    created_at: datetime

class ForumThreadOut(BaseModel):
    id: int
    game_id: int
    game_title: str
    author_id: int
    author_username: str
    title: str
    created_at: datetime
    posts_count: int

class ForumThreadDetailOut(BaseModel):
    id: int
    game_id: int
    game_title: str
    author_id: int
    author_username: str
    title: str
    created_at: datetime
    posts: list[ForumPostOut]

class CreateThreadRequest(BaseModel):
    game_id: int
    title: str
    text: str

class CreatePostRequest(BaseModel):
    text: str
