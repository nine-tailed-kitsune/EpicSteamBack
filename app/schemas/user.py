from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: str | None
    background_url: str | None
    is_admin: bool
    is_owner: bool
    is_banned: bool
    banned_until: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}

class UpdateProfileRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    avatar_url: str | None = None
    background_url: str | None = None