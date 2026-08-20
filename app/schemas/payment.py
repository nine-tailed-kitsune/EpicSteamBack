from pydantic import BaseModel

class CheckoutResponse(BaseModel):
    order_id: int
    confirmation_url: str

class OrderStatusOut(BaseModel):
    id: int
    status: str
    amount: float
