from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book, UserBook, UserGenre
from app.schemas.books import LibraryUpdate


async def save_library_entry(db: AsyncSession, user_id: int, data: LibraryUpdate) -> UserBook:
    book_result = await db.execute(
        select(Book).where(Book.open_library_key == data.book.open_library_key)
    )
    book = book_result.scalar_one_or_none()
    values = data.book.model_dump(exclude={"open_library_key"})
    if book:
        for field, value in values.items():
            setattr(book, field, value)
    else:
        book = Book(open_library_key=data.book.open_library_key, **values)
        db.add(book)
        await db.flush()
    entry_result = await db.execute(
        select(UserBook).where(UserBook.user_id == user_id, UserBook.book_id == book.id)
    )
    entry = entry_result.scalar_one_or_none()
    if entry:
        entry.status, entry.rating, entry.review = data.status, data.rating, data.review
    else:
        entry = UserBook(
            user_id=user_id,
            book_id=book.id,
            status=data.status,
            rating=data.rating,
            review=data.review,
        )
        db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def list_library(db: AsyncSession, user_id: int) -> list[UserBook]:
    result = await db.execute(select(UserBook).where(UserBook.user_id == user_id))
    return list(result.unique().scalars().all())


async def delete_library_entry(db: AsyncSession, user_id: int, work_id: str) -> None:
    book_id = select(Book.id).where(Book.open_library_key == work_id).scalar_subquery()
    await db.execute(
        delete(UserBook).where(UserBook.user_id == user_id, UserBook.book_id == book_id)
    )
    await db.commit()


async def get_genres(db: AsyncSession, user_id: int) -> list[str]:
    result = await db.execute(select(UserGenre.genre).where(UserGenre.user_id == user_id))
    return list(result.scalars().all())


async def set_genres(db: AsyncSession, user_id: int, genres: list[str]) -> list[str]:
    normalized = sorted({genre.strip()[:100] for genre in genres if genre.strip()})
    await db.execute(delete(UserGenre).where(UserGenre.user_id == user_id))
    db.add_all(UserGenre(user_id=user_id, genre=genre) for genre in normalized)
    await db.commit()
    return normalized
