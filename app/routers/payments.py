from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.models.user import User
from app.schemas.payment import CheckoutResponse, OrderStatusOut
from app.auth import get_current_user
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await payment_service.create_payment(current_user, db)

@router.post("/webhook")
async def webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    await payment_service.handle_webhook(payload, db)
    return {"status": "ok"}

@router.get("/orders/{order_id}", response_model=OrderStatusOut)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    order = await payment_service.get_order_status(order_id, current_user, db)
    return OrderStatusOut(id=order.id, status=order.status, amount=order.amount)
