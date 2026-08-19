from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.auth.club_permissions import (
    get_club_membership,
    require_book_manager,
    require_club_editor,
    require_member_manager,
)
from app.database.session import get_db
from app.models.club import BookClub, ClubBookStatus, ClubRole
from app.models.user import User
from app.repositories import clubs as repository
from app.schemas.books import BookResponse
from app.schemas.clubs import (
    ClubBookResponse,
    ClubBookUpdate,
    ClubCreate,
    ClubDetail,
    ClubMemberResponse,
    ClubSummary,
    ClubUpdate,
    RoleUpdate,
)

router = APIRouter(prefix="/clubs", tags=["book clubs"])
Db = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_club(db: AsyncSession, club_id: int) -> BookClub:
    club = await repository.get_club(db, club_id)
    if not club:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book club not found")
    return club


async def summary(db: AsyncSession, club: BookClub) -> ClubSummary:
    books = await repository.club_books(db, club.id)
    current = next((item.book for item in books if item.status == ClubBookStatus.CURRENT), None)
    return ClubSummary(
        **ClubSummary.model_validate(club).model_dump(exclude={"member_count", "current_book"}),
        member_count=await repository.member_count(db, club.id),
        current_book=BookResponse.model_validate(current) if current else None,
    )


@router.get("", response_model=list[ClubSummary])
async def browse_clubs(db: Db, user: CurrentUser) -> list[ClubSummary]:
    del user
    return [await summary(db, club) for club in await repository.list_clubs(db)]


@router.post("", response_model=ClubDetail, status_code=status.HTTP_201_CREATED)
async def create(data: ClubCreate, db: Db, user: CurrentUser) -> ClubDetail:
    try:
        club = await repository.create_club(db, user.id, data)
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "A club with this name already exists"
        ) from error
    return await detail(club.id, db, user)


@router.get("/{club_id}", response_model=ClubDetail)
async def detail(club_id: int, db: Db, user: CurrentUser) -> ClubDetail:
    club = await require_club(db, club_id)
    membership = await get_club_membership(db, club_id, user.id)
    if not club.is_public and not membership:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This club is private")
    base = await summary(db, club)
    members = await repository.club_members(db, club_id)
    books = await repository.club_books(db, club_id)
    return ClubDetail(
        **base.model_dump(),
        members=[ClubMemberResponse.model_validate(member) for member in members],
        books=[ClubBookResponse.model_validate(book) for book in books],
        viewer_role=membership.role if membership else None,
    )


@router.patch("/{club_id}", response_model=ClubDetail)
async def edit(club_id: int, data: ClubUpdate, db: Db, user: CurrentUser) -> ClubDetail:
    club = await require_club(db, club_id)
    await require_club_editor(db, club_id, user.id)
    await repository.update_club(db, club, data)
    return await detail(club_id, db, user)


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove(club_id: int, db: Db, user: CurrentUser) -> Response:
    club = await require_club(db, club_id)
    membership = await get_club_membership(db, club_id, user.id)
    if not membership or membership.role != ClubRole.OWNER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can delete this club")
    await repository.delete_club(db, club)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{club_id}/join", response_model=ClubMemberResponse)
async def join(club_id: int, db: Db, user: CurrentUser) -> ClubMemberResponse:
    club = await require_club(db, club_id)
    if not club.is_public:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This club is private")
    membership = await get_club_membership(db, club_id, user.id)
    if membership:
        return ClubMemberResponse.model_validate(membership)
    return ClubMemberResponse.model_validate(await repository.join_club(db, club_id, user.id))


@router.delete("/{club_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave(club_id: int, db: Db, user: CurrentUser) -> Response:
    membership = await get_club_membership(db, club_id, user.id)
    if not membership:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Club membership not found")
    if membership.role == ClubRole.OWNER:
        raise HTTPException(status.HTTP_409_CONFLICT, "Transfer ownership or delete the club")
    await repository.leave_club(db, membership)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{club_id}/members", response_model=list[ClubMemberResponse])
async def members(club_id: int, db: Db, user: CurrentUser) -> list[ClubMemberResponse]:
    club = await require_club(db, club_id)
    membership = await get_club_membership(db, club_id, user.id)
    if not club.is_public and not membership:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This club is private")
    return [
        ClubMemberResponse.model_validate(item)
        for item in await repository.club_members(db, club_id)
    ]


@router.patch("/{club_id}/members/{member_id}", response_model=ClubMemberResponse)
async def change_role(
    club_id: int, member_id: int, data: RoleUpdate, db: Db, user: CurrentUser
) -> ClubMemberResponse:
    actor = await require_member_manager(db, club_id, user.id)
    members = await repository.club_members(db, club_id)
    target = next((member for member in members if member.id == member_id), None)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Club member not found")
    if actor.role == ClubRole.ADMIN and (
        target.role in {ClubRole.OWNER, ClubRole.ADMIN}
        or data.role in {ClubRole.OWNER, ClubRole.ADMIN}
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can manage admins")
    if data.role == ClubRole.OWNER:
        if actor.role != ClubRole.OWNER or target.id == actor.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owner can transfer ownership")
        actor.role = ClubRole.ADMIN
    elif target.role == ClubRole.OWNER:
        raise HTTPException(status.HTTP_409_CONFLICT, "Transfer ownership to another member")
    target.role = data.role
    await db.commit()
    await db.refresh(target)
    return ClubMemberResponse.model_validate(target)


@router.delete("/{club_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def kick_member(club_id: int, member_id: int, db: Db, user: CurrentUser) -> Response:
    actor = await require_member_manager(db, club_id, user.id)
    members = await repository.club_members(db, club_id)
    target = next((member for member in members if member.id == member_id), None)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Club member not found")
    if target.role == ClubRole.OWNER or (
        actor.role == ClubRole.ADMIN and target.role == ClubRole.ADMIN
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot remove this member")
    await repository.remove_member(db, target)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{club_id}/books", response_model=ClubBookResponse)
async def set_club_book(
    club_id: int, data: ClubBookUpdate, db: Db, user: CurrentUser
) -> ClubBookResponse:
    await require_club(db, club_id)
    await require_book_manager(db, club_id, user.id)
    return ClubBookResponse.model_validate(await repository.save_club_book(db, club_id, data))


@router.delete("/{club_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_club_book(club_id: int, book_id: int, db: Db, user: CurrentUser) -> Response:
    await require_book_manager(db, club_id, user.id)
    await repository.delete_club_book(db, club_id, book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
