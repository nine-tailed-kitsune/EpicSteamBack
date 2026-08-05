from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.game import Game, Screenshot
from app.models.comment import GameComment, ProfileComment
from app.schemas.comment import BanRequest
from app.schemas.game import CreateGameRequest, UpdateGameRequest

async def list_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.id))
    return list(result.scalars().all())

async def ban_user(user_id: int, data: BanRequest, current_user: User, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя заблокировать самого себя")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Нельзя заблокировать администратора")

    user.is_banned = True
    user.banned_until = data.banned_until
    await db.commit()
    await db.refresh(user)
    return user

async def unban_user(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_banned = False
    user.banned_until = None
    await db.commit()
    await db.refresh(user)
    return user

async def make_admin(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Пользователь уже является администратором")

    user.is_admin = True
    await db.commit()
    await db.refresh(user)
    return user

async def remove_admin(user_id: int, current_user: User, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя снять права с себя")

    user.is_admin = False
    await db.commit()
    await db.refresh(user)
    return user

async def create_game(data: CreateGameRequest, db: AsyncSession) -> Game:
    game = Game(
        title=data.title,
        description=data.description,
        price=data.price,
        genre=data.genre,
        release_date=data.release_date,
        header_image=data.header_image,
        trailer_url=data.trailer_url
    )
    db.add(game)
    await db.flush()

    for url in data.screenshots:
        db.add(Screenshot(game_id=game.id, url=url))

    await db.commit()
    await db.refresh(game)

    result = await db.execute(
        select(Game).where(Game.id == game.id).options(selectinload(Game.screenshots))
    )
    return result.scalar_one()

async def update_game(game_id: int, data: UpdateGameRequest, db: AsyncSession) -> Game:
    result = await db.execute(
        select(Game).where(Game.id == game_id).options(selectinload(Game.screenshots))
    )
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    if data.title is not None:
        game.title = data.title
    if data.description is not None:
        game.description = data.description
    if data.price is not None:
        game.price = data.price
    if data.genre is not None:
        game.genre = data.genre
    if data.release_date is not None:
        game.release_date = data.release_date
    if data.header_image is not None:
        game.header_image = data.header_image
    if data.trailer_url is not None:
        game.trailer_url = data.trailer_url

    if data.screenshots is not None:
        for s in list(game.screenshots):
            await db.delete(s)
        await db.flush()
        for url in data.screenshots:
            db.add(Screenshot(game_id=game.id, url=url))

    await db.commit()
    await db.refresh(game)

    result = await db.execute(
        select(Game).where(Game.id == game.id).options(selectinload(Game.screenshots))
    )
    return result.scalar_one()

async def delete_game(game_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")
    await db.delete(game)
    await db.commit()

async def delete_game_comment_admin(comment_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(GameComment).where(GameComment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    await db.delete(comment)
    await db.commit()

async def delete_profile_comment_admin(comment_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(ProfileComment).where(ProfileComment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    await db.delete(comment)
    await db.commit()