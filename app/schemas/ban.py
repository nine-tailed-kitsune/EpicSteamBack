from datetime import datetime
from pydantic import BaseModel

class BanGameRequest(BaseModel):
    banned_until: datetime | None = None

class GameBanOut(BaseModel):
    id: int
    user_id: int
    game_id: int
    banned_until: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}
