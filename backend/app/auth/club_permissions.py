from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.club import BookClubMember, ClubRole

EDIT_ROLES = {ClubRole.OWNER, ClubRole.ADMIN}
MEMBER_MANAGEMENT_ROLES = {ClubRole.OWNER, ClubRole.ADMIN}
BOOK_AND_MEETING_ROLES = {ClubRole.OWNER, ClubRole.ADMIN}
MODERATION_ROLES = {ClubRole.OWNER, ClubRole.ADMIN, ClubRole.MODERATOR}
PARTICIPATION_ROLES = set(ClubRole)


async def get_club_membership(
    db: AsyncSession, club_id: int, user_id: int
) -> BookClubMember | None:
    result = await db.execute(
        select(BookClubMember).where(
            BookClubMember.club_id == club_id, BookClubMember.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def require_club_role(
    db: AsyncSession, club_id: int, user_id: int, allowed_roles: set[ClubRole]
) -> BookClubMember:
    membership = await get_club_membership(db, club_id, user_id)
    if not membership:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Club membership required")
    if membership.role not in allowed_roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient club permissions")
    return membership


async def require_club_editor(db: AsyncSession, club_id: int, user_id: int) -> BookClubMember:
    return await require_club_role(db, club_id, user_id, EDIT_ROLES)


async def require_member_manager(db: AsyncSession, club_id: int, user_id: int) -> BookClubMember:
    return await require_club_role(db, club_id, user_id, MEMBER_MANAGEMENT_ROLES)


async def require_book_manager(db: AsyncSession, club_id: int, user_id: int) -> BookClubMember:
    return await require_club_role(db, club_id, user_id, BOOK_AND_MEETING_ROLES)


async def require_moderator(db: AsyncSession, club_id: int, user_id: int) -> BookClubMember:
    return await require_club_role(db, club_id, user_id, MODERATION_ROLES)


async def require_participant(db: AsyncSession, club_id: int, user_id: int) -> BookClubMember:
    return await require_club_role(db, club_id, user_id, PARTICIPATION_ROLES)
