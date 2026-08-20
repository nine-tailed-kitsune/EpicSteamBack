from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.models.user import User
from app.schemas.message import MessageOut, SendMessageRequest, ConversationOut
from app.auth import get_current_user
from app.services import message_service

router = APIRouter(prefix="/messages", tags=["messages"])

def to_message_out(message):
    return MessageOut(
        id=message.id,
        sender_id=message.sender_id,
        sender_username=message.sender.username,
        receiver_id=message.receiver_id,
        receiver_username=message.receiver.username,
        text=message.text,
        is_read=message.is_read,
        created_at=message.created_at
    )

@router.get("", response_model=list[ConversationOut])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await message_service.get_conversations(current_user, db)

@router.get("/{user_id}", response_model=list[MessageOut])
async def get_conversation(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    messages = await message_service.get_conversation(current_user, user_id, db)
    return [to_message_out(message) for message in messages]

@router.post("/{user_id}", response_model=MessageOut, status_code=201)
async def send_message(
    user_id: int,
    data: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    message = await message_service.send_message(current_user, user_id, data, db)
    return to_message_out(message)
