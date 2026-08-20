from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.game import Game
from app.models.user import User
from app.models.forum import ForumThread, ForumPost
from app.schemas.forum import CreateThreadRequest, CreatePostRequest

async def list_threads(game_id: int | None, db: AsyncSession) -> list[ForumThread]:
    query = select(ForumThread).options(
        selectinload(ForumThread.game),
        selectinload(ForumThread.author),
        selectinload(ForumThread.posts)
    ).order_by(ForumThread.created_at.desc())

    if game_id is not None:
        query = query.where(ForumThread.game_id == game_id)

    result = await db.execute(query)
    return list(result.scalars().all())

async def get_thread(thread_id: int, db: AsyncSession) -> ForumThread:
    result = await db.execute(
        select(ForumThread)
        .where(ForumThread.id == thread_id)
        .options(
            selectinload(ForumThread.game),
            selectinload(ForumThread.author),
            selectinload(ForumThread.posts).selectinload(ForumPost.author)
        )
    )
    thread = result.scalar_one_or_none()
    if not thread:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    return thread

async def create_thread(data: CreateThreadRequest, current_user: User, db: AsyncSession) -> ForumThread:
    result = await db.execute(select(Game).where(Game.id == data.game_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Игра не найдена")

    thread = ForumThread(game_id=data.game_id, author_id=current_user.id, title=data.title)
    db.add(thread)
    await db.flush()

    post = ForumPost(thread_id=thread.id, author_id=current_user.id, text=data.text)
    db.add(post)
    await db.commit()
    return await get_thread(thread.id, db)

async def add_post(thread_id: int, data: CreatePostRequest, current_user: User, db: AsyncSession) -> ForumThread:
    result = await db.execute(select(ForumThread).where(ForumThread.id == thread_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Тема не найдена")

    post = ForumPost(thread_id=thread_id, author_id=current_user.id, text=data.text)
    db.add(post)
    await db.commit()
    return await get_thread(thread_id, db)

async def delete_thread(thread_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(ForumThread).where(ForumThread.id == thread_id))
    thread = result.scalar_one_or_none()
    if not thread:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    await db.delete(thread)
    await db.commit()
