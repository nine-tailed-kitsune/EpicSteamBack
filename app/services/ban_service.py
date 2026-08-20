from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ban import GameBan

async def get_active_game_ban(user_id: int, game_id: int, db: AsyncSession) -> GameBan | None:
    result = await db.execute(
        select(GameBan).where(GameBan.user_id == user_id, GameBan.game_id == game_id)
    )
    ban = result.scalar_one_or_none()
    if not ban:
        return None
    if ban.banned_until is not None and ban.banned_until <= datetime.now(timezone.utc):
        return None
    return ban
