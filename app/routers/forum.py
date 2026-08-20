from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.models.user import User
from app.schemas.forum import (
    ForumThreadOut,
    ForumThreadDetailOut,
    ForumPostOut,
    CreateThreadRequest,
    CreatePostRequest,
)
from app.auth import get_current_user
from app.services import forum_service

router = APIRouter(prefix="/forum", tags=["forum"])

def to_thread_out(thread):
    return ForumThreadOut(
        id=thread.id,
        game_id=thread.game_id,
        game_title=thread.game.title,
        author_id=thread.author_id,
        author_username=thread.author.username,
        title=thread.title,
        created_at=thread.created_at,
        posts_count=len(thread.posts)
    )

def to_thread_detail_out(thread):
    return ForumThreadDetailOut(
        id=thread.id,
        game_id=thread.game_id,
        game_title=thread.game.title,
        author_id=thread.author_id,
        author_username=thread.author.username,
        title=thread.title,
        created_at=thread.created_at,
        posts=[
            ForumPostOut(
                id=post.id,
                author_id=post.author_id,
                author_username=post.author.username,
                text=post.text,
                created_at=post.created_at
            )
            for post in thread.posts
        ]
    )

@router.get("/threads", response_model=list[ForumThreadOut])
async def list_threads(
    game_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    threads = await forum_service.list_threads(game_id, db)
    return [to_thread_out(thread) for thread in threads]

@router.get("/threads/{thread_id}", response_model=ForumThreadDetailOut)
async def get_thread(thread_id: int, db: AsyncSession = Depends(get_db)):
    thread = await forum_service.get_thread(thread_id, db)
    return to_thread_detail_out(thread)

@router.post("/threads", response_model=ForumThreadDetailOut, status_code=201)
async def create_thread(
    data: CreateThreadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    thread = await forum_service.create_thread(data, current_user, db)
    return to_thread_detail_out(thread)

@router.post("/threads/{thread_id}/posts", response_model=ForumThreadDetailOut, status_code=201)
async def add_post(
    thread_id: int,
    data: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    thread = await forum_service.add_post(thread_id, data, current_user, db)
    return to_thread_detail_out(thread)
