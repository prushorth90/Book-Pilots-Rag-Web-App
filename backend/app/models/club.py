from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.book import Book
from app.models.user import User


class ClubRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    MEMBER = "MEMBER"


class ClubBookStatus(str, Enum):
    CURRENT = "CURRENT"
    UPCOMING = "UPCOMING"
    COMPLETED = "COMPLETED"


class BookClub(Base):
    __tablename__ = "book_clubs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class BookClubMember(Base):
    __tablename__ = "book_club_members"
    __table_args__ = (UniqueConstraint("club_id", "user_id", name="uq_club_member"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(
        ForeignKey("book_clubs.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[ClubRole] = mapped_column(
        SqlEnum(ClubRole, native_enum=False), default=ClubRole.MEMBER
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user: Mapped[User] = relationship(lazy="joined")


class ClubBook(Base):
    __tablename__ = "club_books"
    __table_args__ = (UniqueConstraint("club_id", "book_id", name="uq_club_book"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(
        ForeignKey("book_clubs.id", ondelete="CASCADE"), index=True
    )
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)
    status: Mapped[ClubBookStatus] = mapped_column(
        SqlEnum(ClubBookStatus, native_enum=False), default=ClubBookStatus.UPCOMING
    )
    book: Mapped[Book] = relationship(lazy="joined")
