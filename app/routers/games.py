from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.models.user import User
from app.schemas.game import GameOut, GameDetailOut
from app.schemas.comment import GameCommentOut, AddCommentRequest
from app.auth import get_current_user
from app.services import game_service

router = APIRouter(prefix="/games", tags=["games"])

@router.get("", response_model=list[GameOut])
async def get_games(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await game_service.get_all_games(skip, limit, db)

@router.get("/search", response_model=list[GameOut])
async def search_games(
    q: str = Query(""),
    genre: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await game_service.search_games(q, genre, min_price, max_price, db)

@router.get("/{game_id}", response_model=GameDetailOut)
async def get_game(game_id: int, db: AsyncSession = Depends(get_db)):
    return await game_service.get_game_by_id(game_id, db)

@router.post("/{game_id}/comments", response_model=GameCommentOut, status_code=201)
async def add_comment(
    game_id: int,
    data: AddCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await game_service.add_game_comment(game_id, data, current_user, db)

@router.delete("/{game_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
    game_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await game_service.delete_game_comment(game_id, comment_id, current_user, db)