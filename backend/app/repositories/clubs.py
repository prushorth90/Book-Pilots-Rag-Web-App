from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.club import BookClub, BookClubMember, ClubBook, ClubBookStatus, ClubRole
from app.schemas.clubs import ClubBookUpdate, ClubCreate, ClubUpdate


async def create_club(db: AsyncSession, user_id: int, data: ClubCreate) -> BookClub:
    club = BookClub(**data.model_dump())
    db.add(club)
    await db.flush()
    db.add(BookClubMember(club_id=club.id, user_id=user_id, role=ClubRole.OWNER))
    await db.commit()
    await db.refresh(club)
    return club


async def get_club(db: AsyncSession, club_id: int) -> BookClub | None:
    return (await db.execute(select(BookClub).where(BookClub.id == club_id))).scalar_one_or_none()


async def list_clubs(db: AsyncSession) -> list[BookClub]:
    return list((await db.execute(select(BookClub).order_by(BookClub.created_at.desc()))).scalars())


async def update_club(db: AsyncSession, club: BookClub, data: ClubUpdate) -> BookClub:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(club, field, value)
    await db.commit()
    await db.refresh(club)
    return club


async def club_members(db: AsyncSession, club_id: int) -> list[BookClubMember]:
    result = await db.execute(
        select(BookClubMember)
        .where(BookClubMember.club_id == club_id)
        .order_by(BookClubMember.joined_at)
    )
    return list(result.unique().scalars())


async def club_books(db: AsyncSession, club_id: int) -> list[ClubBook]:
    result = await db.execute(select(ClubBook).where(ClubBook.club_id == club_id))
    return list(result.unique().scalars())


async def member_count(db: AsyncSession, club_id: int) -> int:
    return int(
        await db.scalar(
            select(func.count())
            .select_from(BookClubMember)
            .where(BookClubMember.club_id == club_id)
        )
        or 0
    )


async def join_club(db: AsyncSession, club_id: int, user_id: int) -> BookClubMember:
    membership = BookClubMember(club_id=club_id, user_id=user_id, role=ClubRole.MEMBER)
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


async def leave_club(db: AsyncSession, membership: BookClubMember) -> None:
    await db.delete(membership)
    await db.commit()


async def remove_member(db: AsyncSession, membership: BookClubMember) -> None:
    await db.delete(membership)
    await db.commit()


async def save_club_book(db: AsyncSession, club_id: int, data: ClubBookUpdate) -> ClubBook:
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
    if data.status == ClubBookStatus.CURRENT:
        current = await db.execute(
            select(ClubBook).where(
                ClubBook.club_id == club_id, ClubBook.status == ClubBookStatus.CURRENT
            )
        )
        for existing in current.scalars():
            existing.status = ClubBookStatus.COMPLETED
    club_book_result = await db.execute(
        select(ClubBook).where(ClubBook.club_id == club_id, ClubBook.book_id == book.id)
    )
    club_book = club_book_result.scalar_one_or_none()
    if club_book:
        club_book.status = data.status
    else:
        club_book = ClubBook(club_id=club_id, book_id=book.id, status=data.status)
        db.add(club_book)
    await db.commit()
    await db.refresh(club_book)
    return club_book


async def delete_club(db: AsyncSession, club: BookClub) -> None:
    await db.delete(club)
    await db.commit()


async def delete_club_book(db: AsyncSession, club_id: int, book_id: int) -> None:
    await db.execute(
        delete(ClubBook).where(ClubBook.club_id == club_id, ClubBook.book_id == book_id)
    )
    await db.commit()
