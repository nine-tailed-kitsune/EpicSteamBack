from sqlalchemy import Integer, ForeignKey, Table, Column
from app.models.base import Base

wishlist_items = Table(
    "wishlist_items",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("game_id", Integer, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
)
