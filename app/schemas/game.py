from datetime import datetime
from pydantic import BaseModel
from app.schemas.comment import GameCommentOut

class ScreenshotOut(BaseModel):
    id: int
    url: str
    model_config = {"from_attributes": True}

class GameOut(BaseModel):
    id: int
    title: str
    description: str | None
    price: float
    genre: str | None
    release_date: datetime | None
    header_image: str | None
    trailer_url: str | None
    created_at: datetime
    screenshots: list[ScreenshotOut] = []
    model_config = {"from_attributes": True}

class GameDetailOut(GameOut):
    comments: list[GameCommentOut] = []

class CreateGameRequest(BaseModel):
    title: str
    description: str | None = None
    price: float
    genre: str | None = None
    release_date: datetime | None = None
    header_image: str | None = None
    trailer_url: str | None = None
    screenshots: list[str] = []

class UpdateGameRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    genre: str | None = None
    release_date: datetime | None = None
    header_image: str | None = None
    trailer_url: str | None = None
    screenshots: list[str] | None = None