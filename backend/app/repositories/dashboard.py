from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import UserBook, UserGenre
from app.models.club import BookClub, BookClubMember, ClubBook, ClubBookStatus
from app.models.communication import ChatMessage


async def reading_and_genres(db: AsyncSession, user_id: int) -> tuple[list[UserBook], list[str]]:
    library_result = await db.execute(
        select(UserBook).where(UserBook.user_id == user_id).order_by(UserBook.id.desc())
    )
    genre_result = await db.execute(
        select(UserGenre.genre).where(UserGenre.user_id == user_id).order_by(UserGenre.genre)
    )
    return list(library_result.unique().scalars()), list(genre_result.scalars())


async def club_overview(
    db: AsyncSession, user_id: int
) -> list[tuple[BookClubMember, BookClub, ClubBook | None, int]]:
    member_counts = (
        select(BookClubMember.club_id, func.count(BookClubMember.id).label("member_count"))
        .group_by(BookClubMember.club_id)
        .subquery()
    )
    result = await db.execute(
        select(BookClubMember, BookClub, ClubBook, member_counts.c.member_count)
        .join(BookClub, BookClub.id == BookClubMember.club_id)
        .outerjoin(
            ClubBook,
            (ClubBook.club_id == BookClub.id) & (ClubBook.status == ClubBookStatus.CURRENT),
        )
        .join(member_counts, member_counts.c.club_id == BookClub.id)
        .where(BookClubMember.user_id == user_id)
        .order_by(BookClub.created_at.desc())
    )
    return [(row[0], row[1], row[2], int(row[3])) for row in result.unique().all()]


async def recent_messages(
    db: AsyncSession, club_ids: list[int], limit: int = 6
) -> list[ChatMessage]:
    if not club_ids:
        return []
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.club_id.in_(club_ids))
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    return list(result.unique().scalars())
