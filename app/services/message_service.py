from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.message import Message
from app.schemas.message import SendMessageRequest

async def send_message(sender: User, receiver_id: int, data: SendMessageRequest, db: AsyncSession) -> Message:
    if sender.id == receiver_id:
        raise HTTPException(status_code=400, detail="Нельзя написать сообщение самому себе")

    result = await db.execute(select(User).where(User.id == receiver_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    message = Message(sender_id=sender.id, receiver_id=receiver_id, text=data.text)
    db.add(message)
    await db.commit()
    await db.refresh(message)

    result = await db.execute(
        select(Message)
        .where(Message.id == message.id)
        .options(selectinload(Message.sender), selectinload(Message.receiver))
    )
    return result.scalar_one()

async def get_conversation(current_user: User, other_user_id: int, db: AsyncSession) -> list[Message]:
    result = await db.execute(select(User).where(User.id == other_user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    result = await db.execute(
        select(Message)
        .where(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
            )
        )
        .options(selectinload(Message.sender), selectinload(Message.receiver))
        .order_by(Message.created_at)
    )
    messages = list(result.scalars().all())

    for message in messages:
        if message.receiver_id == current_user.id and not message.is_read:
            message.is_read = True
    await db.commit()

    return messages

async def get_conversations(current_user: User, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Message)
        .where(or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id))
        .options(selectinload(Message.sender), selectinload(Message.receiver))
        .order_by(Message.created_at.desc())
    )
    messages = result.scalars().all()

    conversations = {}
    for message in messages:
        other = message.receiver if message.sender_id == current_user.id else message.sender
        if other.id not in conversations:
            conversations[other.id] = {
                "user_id": other.id,
                "username": other.username,
                "avatar_url": other.avatar_url,
                "last_message": message.text,
                "last_message_at": message.created_at,
                "unread_count": 0
            }
        if message.receiver_id == current_user.id and not message.is_read:
            conversations[other.id]["unread_count"] += 1

    return list(conversations.values())
