from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.friend import FriendRequest

async def get_request_with_users(request_id: int, db: AsyncSession) -> FriendRequest:
    result = await db.execute(
        select(FriendRequest)
        .where(FriendRequest.id == request_id)
        .options(selectinload(FriendRequest.sender), selectinload(FriendRequest.receiver))
    )
    return result.scalar_one()

async def send_friend_request(sender: User, receiver_id: int, db: AsyncSession) -> FriendRequest:
    if sender.id == receiver_id:
        raise HTTPException(status_code=400, detail="Нельзя добавить в друзья самого себя")

    result = await db.execute(select(User).where(User.id == receiver_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    result = await db.execute(
        select(FriendRequest).where(
            or_(
                and_(FriendRequest.sender_id == sender.id, FriendRequest.receiver_id == receiver_id),
                and_(FriendRequest.sender_id == receiver_id, FriendRequest.receiver_id == sender.id)
            ),
            FriendRequest.status != "declined"
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Заявка уже отправлена или вы уже друзья")

    request = FriendRequest(sender_id=sender.id, receiver_id=receiver_id, status="pending")
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return await get_request_with_users(request.id, db)

async def get_incoming_requests(current_user: User, db: AsyncSession) -> list[FriendRequest]:
    result = await db.execute(
        select(FriendRequest)
        .where(FriendRequest.receiver_id == current_user.id, FriendRequest.status == "pending")
        .options(selectinload(FriendRequest.sender), selectinload(FriendRequest.receiver))
        .order_by(FriendRequest.created_at.desc())
    )
    return list(result.scalars().all())

async def respond_to_request(request_id: int, accept: bool, current_user: User, db: AsyncSession) -> FriendRequest:
    result = await db.execute(select(FriendRequest).where(FriendRequest.id == request_id))
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if request.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    request.status = "accepted" if accept else "declined"
    await db.commit()
    return await get_request_with_users(request.id, db)

async def get_friends(current_user: User, db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(FriendRequest)
        .where(
            or_(FriendRequest.sender_id == current_user.id, FriendRequest.receiver_id == current_user.id),
            FriendRequest.status == "accepted"
        )
        .options(selectinload(FriendRequest.sender), selectinload(FriendRequest.receiver))
    )
    requests = result.scalars().all()

    friends = []
    for request in requests:
        friend = request.receiver if request.sender_id == current_user.id else request.sender
        friends.append(friend)
    return friends

async def remove_friend(friend_id: int, current_user: User, db: AsyncSession) -> None:
    result = await db.execute(
        select(FriendRequest).where(
            or_(
                and_(FriendRequest.sender_id == current_user.id, FriendRequest.receiver_id == friend_id),
                and_(FriendRequest.sender_id == friend_id, FriendRequest.receiver_id == current_user.id)
            ),
            FriendRequest.status == "accepted"
        )
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Вы не друзья с этим пользователем")
    await db.delete(request)
    await db.commit()
