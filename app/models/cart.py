from sqlalchemy import Integer, ForeignKey, Table, Column
from app.models.base import Base

cart_items = Table(
    "cart_items",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("game_id", Integer, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
)