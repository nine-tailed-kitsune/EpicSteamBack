from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.game import Game

async def get_wishlist(current_user: User, db: AsyncSession) -> list[Game]:
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.wishlist).selectinload(Game.screenshots),
            selectinload(User.wishlist).selectinload(Game.category)
        )
    )
    return result.scalar_one().wishlist

async def add_to_wishlist(game_id: int, current_user: User, db: AsyncSession) -> dict:
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.wishlist))
    )
    user = result.scalar_one()

    if any(g.id == game_id for g in user.wishlist):
        raise HTTPException(status_code=400, detail="Игра уже в списке желаемого")

    user.wishlist.append(game)
    await db.commit()
    return {"detail": f"Игра «{game.title}» добавлена в список желаемого"}

async def remove_from_wishlist(game_id: int, current_user: User, db: AsyncSession) -> None:
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.wishlist))
    )
    user = result.scalar_one()

    game = next((g for g in user.wishlist if g.id == game_id), None)
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена в списке желаемого")

    user.wishlist.remove(game)
    await db.commit()
