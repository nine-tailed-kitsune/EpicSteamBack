from pydantic import BaseModel

class CheckoutResponse(BaseModel):
    order_id: int | None
    confirmation_url: str | None

class OrderStatusOut(BaseModel):
    id: int
    status: str
    amount: float
