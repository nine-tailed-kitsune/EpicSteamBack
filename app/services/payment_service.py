import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from yookassa import Configuration, Payment as YooPayment
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.purchase import Purchase
from app.payment_config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, FRONTEND_URL

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

async def create_payment(current_user: User, db: AsyncSession) -> dict:
    result = await db.execute(
        select(User).where(User.id == current_user.id).options(selectinload(User.cart))
    )
    user = result.scalar_one()

    if not user.cart:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    total = sum(game.price for game in user.cart)

    if total <= 0:
        for game in user.cart:
            db.add(Purchase(user_id=user.id, game_id=game.id, price_paid=game.price))
        user.cart.clear()
        await db.commit()
        return {"order_id": None, "confirmation_url": None}

    order = Order(user_id=user.id, amount=total, status="pending")
    db.add(order)
    await db.flush()

    for game in user.cart:
        db.add(OrderItem(order_id=order.id, game_id=game.id, price=game.price))

    await db.commit()

    idempotence_key = str(uuid.uuid4())
    payment = YooPayment.create({
        "amount": {"value": f"{total:.2f}", "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": f"{FRONTEND_URL}/payment/result?order_id={order.id}",
        },
        "capture": True,
        "description": f"Заказ №{order.id} в Epic Steam",
        "metadata": {"order_id": str(order.id)},
    }, idempotence_key)

    order.payment_id = payment.id
    await db.commit()

    return {"order_id": order.id, "confirmation_url": payment.confirmation.confirmation_url}

async def handle_webhook(payload: dict, db: AsyncSession) -> None:
    payment_data = payload.get("object", {})
    payment_id = payment_data.get("id")
    if not payment_id:
        return

    yoo_payment = YooPayment.find_one(payment_id)
    if yoo_payment.status != "succeeded":
        return

    order_id = yoo_payment.metadata.get("order_id")
    if not order_id:
        return

    result = await db.execute(
        select(Order).where(Order.id == int(order_id)).options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order or order.status == "succeeded":
        return

    for item in order.items:
        db.add(Purchase(user_id=order.user_id, game_id=item.game_id, price_paid=item.price))

    order.status = "succeeded"

    result = await db.execute(
        select(User).where(User.id == order.user_id).options(selectinload(User.cart))
    )
    user = result.scalar_one()
    user.cart.clear()

    await db.commit()

async def get_order_status(order_id: int, current_user: User, db: AsyncSession) -> Order:
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order
