from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.game import Game
from app.models.comment import GameComment
from app.models.user import User
from app.schemas.game import GameDetailOut, ScreenshotOut
from app.schemas.comment import GameCommentOut, AddCommentRequest

async def get_all_games(skip: int, limit: int, db: AsyncSession) -> list[Game]:
    result = await db.execute(
        select(Game)
        .options(selectinload(Game.screenshots), selectinload(Game.category))
        .order_by(Game.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

def build_search_filters(q: str, category_id: int | None, min_price: float | None, max_price: float | None):
    filters = []
    if q:
        filters.append(Game.title.ilike(f"%{q}%"))
    if category_id is not None:
        filters.append(Game.category_id == category_id)
    if min_price is not None:
        filters.append(Game.price >= min_price)
    if max_price is not None:
        filters.append(Game.price <= max_price)
    return filters

async def search_games(
    q: str,
    category_id: int | None,
    min_price: float | None,
    max_price: float | None,
    db: AsyncSession,
    skip: int | None = None,
    limit: int | None = None
) -> list[Game]:
    filters = build_search_filters(q, category_id, min_price, max_price)
    query = select(Game).options(selectinload(Game.screenshots), selectinload(Game.category))
    for condition in filters:
        query = query.where(condition)

    query = query.order_by(Game.created_at.desc())
    if skip is not None:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())

async def count_search_games(
    q: str,
    category_id: int | None,
    min_price: float | None,
    max_price: float | None,
    db: AsyncSession
) -> int:
    filters = build_search_filters(q, category_id, min_price, max_price)
    query = select(func.count()).select_from(Game)
    for condition in filters:
        query = query.where(condition)

    result = await db.execute(query)
    return result.scalar_one()

async def get_game_by_id(game_id: int, db: AsyncSession) -> GameDetailOut:
    result = await db.execute(
        select(Game)
        .where(Game.id == game_id)
        .options(
            selectinload(Game.screenshots),
            selectinload(Game.category),
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
        category=game.category,
        release_date=game.release_date,
        header_image=game.header_image,
        trailer_url=game.trailer_url,
        requirements=game.requirements,
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
