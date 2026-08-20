from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.models.user import User
from app.schemas.friend import FriendRequestOut, FriendOut
from app.auth import get_current_user
from app.services import friend_service

router = APIRouter(prefix="/friends", tags=["friends"])

def to_request_out(request):
    return FriendRequestOut(
        id=request.id,
        sender_id=request.sender_id,
        sender_username=request.sender.username,
        receiver_id=request.receiver_id,
        receiver_username=request.receiver.username,
        status=request.status,
        created_at=request.created_at
    )

@router.get("", response_model=list[FriendOut])
async def get_friends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await friend_service.get_friends(current_user, db)

@router.get("/requests", response_model=list[FriendRequestOut])
async def get_incoming_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    requests = await friend_service.get_incoming_requests(current_user, db)
    return [to_request_out(request) for request in requests]

@router.post("/requests/{user_id}", response_model=FriendRequestOut, status_code=201)
async def send_friend_request(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    request = await friend_service.send_friend_request(current_user, user_id, db)
    return to_request_out(request)

@router.post("/requests/{request_id}/accept", response_model=FriendRequestOut)
async def accept_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    request = await friend_service.respond_to_request(request_id, True, current_user, db)
    return to_request_out(request)

@router.post("/requests/{request_id}/decline", response_model=FriendRequestOut)
async def decline_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    request = await friend_service.respond_to_request(request_id, False, current_user, db)
    return to_request_out(request)

@router.delete("/{user_id}", status_code=204)
async def remove_friend(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await friend_service.remove_friend(user_id, current_user, db)
