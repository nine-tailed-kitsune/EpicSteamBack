from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.models.user import User
from app.schemas.user import UserOut
from app.schemas.comment import BanRequest
from app.schemas.game import GameOut, CreateGameRequest, UpdateGameRequest
from app.auth import get_current_admin
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await admin_service.list_all_users(db)

@router.post("/users/{user_id}/ban", response_model=UserOut)
async def ban_user(
    user_id: int,
    data: BanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await admin_service.ban_user(user_id, data, current_user, db)

@router.post("/users/{user_id}/unban", response_model=UserOut)
async def unban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await admin_service.unban_user(user_id, db)

@router.post("/users/{user_id}/make-admin", response_model=UserOut)
async def make_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await admin_service.make_admin(user_id, db)

@router.post("/users/{user_id}/remove-admin", response_model=UserOut)
async def remove_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await admin_service.remove_admin(user_id, current_user, db)

@router.post("/games", response_model=GameOut, status_code=201)
async def create_game(
    data: CreateGameRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await admin_service.create_game(data, db)

@router.patch("/games/{game_id}", response_model=GameOut)
async def update_game(
    game_id: int,
    data: UpdateGameRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await admin_service.update_game(game_id, data, db)

@router.delete("/games/{game_id}", status_code=204)
async def delete_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    await admin_service.delete_game(game_id, db)

@router.delete("/game-comments/{comment_id}", status_code=204)
async def delete_game_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    await admin_service.delete_game_comment_admin(comment_id, db)

@router.delete("/profile-comments/{comment_id}", status_code=204)
async def delete_profile_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    await admin_service.delete_profile_comment_admin(comment_id, db)