from __future__ import annotations

from enum import Enum
from typing import Optional

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ReadingStatus(str, Enum):
    WANT_TO_READ = "WANT_TO_READ"
    READING = "READING"
    READ = "READ"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    open_library_key: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    author: Mapped[str] = mapped_column(String(500), default="Unknown author")
    description: Mapped[Optional[str]] = mapped_column(Text)
    isbn: Mapped[Optional[str]] = mapped_column(String(32))
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500))
    publication_year: Mapped[Optional[int]] = mapped_column(Integer)
    genres: Mapped[list[str]] = mapped_column(JSON, default=list)
    average_rating: Mapped[Optional[float]] = mapped_column(Float)


class UserBook(Base):
    __tablename__ = "user_books"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_user_book"),
        CheckConstraint("rating IS NULL OR (rating >= 1 AND rating <= 5)", name="ck_rating_1_5"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)
    status: Mapped[ReadingStatus] = mapped_column(
        SqlEnum(ReadingStatus, native_enum=False), default=ReadingStatus.WANT_TO_READ
    )
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    review: Mapped[Optional[str]] = mapped_column(Text)
    book: Mapped[Book] = relationship(lazy="joined")


class UserGenre(Base):
    __tablename__ = "user_genres"
    __table_args__ = (UniqueConstraint("user_id", "genre", name="uq_user_genre"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    genre: Mapped[str] = mapped_column(String(100))
