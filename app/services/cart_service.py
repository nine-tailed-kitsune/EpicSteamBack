from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.game import Game
from app.models.purchase import Purchase

async def get_cart(current_user: User, db: AsyncSession) -> list[Game]:
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.cart).selectinload(Game.screenshots),
            selectinload(User.cart).selectinload(Game.category)
        )
    )
    user = result.scalar_one()
    return user.cart

async def add_to_cart(game_id: int, current_user: User, db: AsyncSession) -> dict:
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    result = await db.execute(
        select(Purchase).where(Purchase.user_id == current_user.id, Purchase.game_id == game_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Игра уже есть в вашей библиотеке")

    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.cart))
    )
    user = result.scalar_one()

    if any(g.id == game_id for g in user.cart):
        raise HTTPException(status_code=400, detail="Игра уже в корзине")

    user.cart.append(game)
    await db.commit()
    return {"detail": f"Игра «{game.title}» добавлена в корзину"}

async def remove_from_cart(game_id: int, current_user: User, db: AsyncSession) -> None:
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.cart))
    )
    user = result.scalar_one()

    game = next((g for g in user.cart if g.id == game_id), None)
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена в корзине")

    user.cart.remove(game)
    await db.commit()

async def clear_cart(current_user: User, db: AsyncSession) -> dict:
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.cart))
    )
    user = result.scalar_one()
    user.cart.clear()
    await db.commit()
    return {"detail": "Корзина очищена"}

async def checkout(current_user: User, db: AsyncSession) -> dict:
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.cart))
    )
    user = result.scalar_one()

    if not user.cart:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    for game in user.cart:
        db.add(Purchase(user_id=user.id, game_id=game.id, price_paid=game.price))

    user.cart.clear()
    await db.commit()
    return {"detail": "Покупка оформлена, игры добавлены в вашу библиотеку"}