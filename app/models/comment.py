from datetime import datetime, timezone
from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class GameComment(Base):
    __tablename__ = "game_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    game = relationship("Game", back_populates="comments")
    author = relationship("User", back_populates="game_comments")

class ProfileComment(Base):
    __tablename__ = "profile_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    profile_owner = relationship("User", foreign_keys=[profile_owner_id], back_populates="profile_comments_received")
    author = relationship("User", foreign_keys=[author_id], back_populates="profile_comments_written")