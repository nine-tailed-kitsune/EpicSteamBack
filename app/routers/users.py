from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UpdateProfileRequest
from app.schemas.comment import ProfileCommentOut, AddCommentRequest
from app.schemas.game import GameOut
from app.auth import get_current_user
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/search", response_model=list[UserOut])
async def search_users(q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    return await user_service.search_users(q, db)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_service.get_user_by_id(user_id, db)

@router.get("/{user_id}/library", response_model=list[GameOut])
async def get_user_library(
    user_id: int,
    skip: int | None = Query(None, ge=0),
    limit: int | None = Query(None, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await user_service.get_user_library(user_id, db, skip, limit)

@router.get("/{user_id}/library/count")
async def count_user_library(user_id: int, db: AsyncSession = Depends(get_db)):
    total = await user_service.count_user_library(user_id, db)
    return {"total": total}

@router.get("/{user_id}/wishlist", response_model=list[GameOut])
async def get_user_wishlist(
    user_id: int,
    skip: int | None = Query(None, ge=0),
    limit: int | None = Query(None, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await user_service.get_user_wishlist(user_id, db, skip, limit)

@router.get("/{user_id}/wishlist/count")
async def count_user_wishlist(user_id: int, db: AsyncSession = Depends(get_db)):
    total = await user_service.count_user_wishlist(user_id, db)
    return {"total": total}

@router.patch("/me", response_model=UserOut)
async def update_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await user_service.update_profile(data, current_user, db)

@router.get("/{user_id}/comments", response_model=list[ProfileCommentOut])
async def get_profile_comments(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_service.get_profile_comments(user_id, db)

@router.post("/{user_id}/comments", response_model=ProfileCommentOut, status_code=201)
async def add_profile_comment(
    user_id: int,
    data: AddCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await user_service.add_profile_comment(user_id, data, current_user, db)

@router.delete("/{user_id}/comments/{comment_id}", status_code=204)
async def delete_profile_comment(
    user_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await user_service.delete_profile_comment(user_id, comment_id, current_user, db)
