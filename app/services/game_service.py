from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.game import Game
from app.models.comment import GameComment
from app.models.user import User
from app.schemas.game import GameDetailOut, ScreenshotOut
from app.schemas.comment import GameCommentOut, AddCommentRequest

async def get_all_games(skip: int, limit: int, db: AsyncSession) -> list[Game]:
    result = await db.execute(
        select(Game)
        .options(selectinload(Game.screenshots))
        .order_by(Game.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

async def search_games(
    q: str,
    genre: str | None,
    min_price: float | None,
    max_price: float | None,
    db: AsyncSession
) -> list[Game]:
    query = select(Game).options(selectinload(Game.screenshots))

    if q:
        query = query.where(Game.title.ilike(f"%{q}%"))
    if genre:
        query = query.where(Game.genre.ilike(f"%{genre}%"))
    if min_price is not None:
        query = query.where(Game.price >= min_price)
    if max_price is not None:
        query = query.where(Game.price <= max_price)

    result = await db.execute(query.order_by(Game.created_at.desc()))
    return list(result.scalars().all())

async def get_game_by_id(game_id: int, db: AsyncSession) -> GameDetailOut:
    result = await db.execute(
        select(Game)
        .where(Game.id == game_id)
        .options(
            selectinload(Game.screenshots),
            selectinload(Game.comments).selectinload(GameComment.author)
        )
    )
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    comments_out = [
        GameCommentOut(
            id=c.id,
            author_id=c.author_id,
            author_username=c.author.username,
            text=c.text,
            created_at=c.created_at
        )
        for c in sorted(game.comments, key=lambda x: x.created_at, reverse=True)
    ]

    return GameDetailOut(
        id=game.id,
        title=game.title,
        description=game.description,
        price=game.price,
        genre=game.genre,
        release_date=game.release_date,
        header_image=game.header_image,
        trailer_url=game.trailer_url,
        created_at=game.created_at,
        screenshots=[ScreenshotOut(id=s.id, url=s.url) for s in game.screenshots],
        comments=comments_out
    )

async def add_game_comment(
    game_id: int,
    data: AddCommentRequest,
    current_user: User,
    db: AsyncSession
) -> GameCommentOut:
    result = await db.execute(select(Game).where(Game.id == game_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Игра не найдена")

    comment = GameComment(game_id=game_id, author_id=current_user.id, text=data.text)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return GameCommentOut(
        id=comment.id,
        author_id=comment.author_id,
        author_username=current_user.username,
        text=comment.text,
        created_at=comment.created_at
    )

async def delete_game_comment(
    game_id: int,
    comment_id: int,
    current_user: User,
    db: AsyncSession
) -> None:
    result = await db.execute(
        select(GameComment).where(
            GameComment.id == comment_id,
            GameComment.game_id == game_id
        )
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")

    await db.delete(comment)
    await db.commit()