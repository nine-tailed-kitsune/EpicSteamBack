from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.models.user import User
from app.schemas.game import GameOut
from app.auth import get_current_user
from app.services import wishlist_service

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

@router.get("", response_model=list[GameOut])
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await wishlist_service.get_wishlist(current_user, db)

@router.post("/{game_id}", status_code=201)
async def add_to_wishlist(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await wishlist_service.add_to_wishlist(game_id, current_user, db)

@router.delete("/{game_id}", status_code=204)
async def remove_from_wishlist(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await wishlist_service.remove_from_wishlist(game_id, current_user, db)
