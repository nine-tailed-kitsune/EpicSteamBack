from datetime import datetime, date
from pydantic import BaseModel
from app.schemas.comment import GameCommentOut
from app.schemas.category import CategoryOut

class ScreenshotOut(BaseModel):
    id: int
    url: str
    model_config = {"from_attributes": True}

class GameOut(BaseModel):
    id: int
    title: str
    description: str | None
    price: float
    category: CategoryOut | None
    release_date: date | None
    header_image: str | None
    trailer_url: str | None
    requirements: str | None
    created_at: datetime
    screenshots: list[ScreenshotOut] = []
    model_config = {"from_attributes": True}

class GameDetailOut(GameOut):
    comments: list[GameCommentOut] = []

class CreateGameRequest(BaseModel):
    title: str
    description: str | None = None
    price: float
    category_id: int | None = None
    release_date: date | None = None
    header_image: str | None = None
    trailer_url: str | None = None
    requirements: str | None = None
    screenshots: list[str] = []

class UpdateGameRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    category_id: int | None = None
    release_date: date | None = None
    header_image: str | None = None
    trailer_url: str | None = None
    requirements: str | None = None
    screenshots: list[str] | None = None
