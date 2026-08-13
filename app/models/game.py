from datetime import datetime, date
from sqlalchemy import Integer, String, Float, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.cart import cart_items

class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    genre: Mapped[str | None] = mapped_column(String(100))
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    header_image: Mapped[str | None] = mapped_column(String(500))
    trailer_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    screenshots = relationship("Screenshot", back_populates="game", cascade="all, delete-orphan")
    comments = relationship("GameComment", back_populates="game", cascade="all, delete-orphan")
    in_carts = relationship("User", secondary=cart_items, back_populates="cart")

class Screenshot(Base):
    __tablename__ = "screenshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    game = relationship("Game", back_populates="screenshots")