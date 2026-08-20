from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.models.user import User
from app.schemas.game import GameOut
from app.auth import get_current_user
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("", response_model=list[GameOut])
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await cart_service.get_cart(current_user, db)

@router.post("/checkout", status_code=200)
async def checkout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await cart_service.checkout(current_user, db)

@router.delete("/clear", status_code=200)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await cart_service.clear_cart(current_user, db)

@router.post("/{game_id}", status_code=201)
async def add_to_cart(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await cart_service.add_to_cart(game_id, current_user, db)

@router.delete("/{game_id}", status_code=204)
async def remove_from_cart(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await cart_service.remove_from_cart(game_id, current_user, db)
