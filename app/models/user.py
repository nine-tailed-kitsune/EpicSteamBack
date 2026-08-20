from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.cart import cart_items
from app.models.wishlist import wishlist_items

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    background_url: Mapped[str | None] = mapped_column(String(500))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    banned_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cart = relationship("Game", secondary=cart_items, back_populates="in_carts")
    wishlist = relationship("Game", secondary=wishlist_items, back_populates="wished_by")
    purchases = relationship("Purchase", back_populates="user", cascade="all, delete-orphan")
    game_comments = relationship("GameComment", back_populates="author", cascade="all, delete-orphan")
    profile_comments_written = relationship("ProfileComment", foreign_keys="ProfileComment.author_id", back_populates="author", cascade="all, delete-orphan")
    profile_comments_received = relationship("ProfileComment", foreign_keys="ProfileComment.profile_owner_id", back_populates="profile_owner", cascade="all, delete-orphan")
    sent_friend_requests = relationship("FriendRequest", foreign_keys="FriendRequest.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_friend_requests = relationship("FriendRequest", foreign_keys="FriendRequest.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
