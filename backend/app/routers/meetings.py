from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.auth.club_permissions import require_book_manager, require_participant
from app.database.session import get_db
from app.models.meeting import Meeting, MeetingAttendee
from app.models.user import User
from app.repositories import meetings as repository
from app.schemas.meetings import (
    AttendeeResponse,
    AvailabilityResponse,
    AvailabilityUpdate,
    MeetingCreate,
    MeetingResponse,
    MeetingUpdate,
    RsvpUpdate,
    utc_datetime,
)

router = APIRouter(tags=["calendar and meetings"])
Db = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def meeting_response(meeting: Meeting, user_id: int) -> MeetingResponse:
    viewer = next((item.status for item in meeting.attendees if item.user_id == user_id), None)
    return MeetingResponse(
        id=meeting.id,
        club_id=meeting.club_id,
        club_name=meeting.club.name,
        creator_id=meeting.creator_id,
        organizer=meeting.creator,
        title=meeting.title,
        description=meeting.description,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        timezone=meeting.timezone,
        location=meeting.location,
        status=meeting.status,
        created_at=meeting.created_at,
        attendees=[AttendeeResponse.model_validate(item) for item in meeting.attendees],
        viewer_rsvp=viewer,
    )


async def require_meeting(db: AsyncSession, meeting_id: int) -> Meeting:
    meeting = await repository.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meeting not found")
    return meeting


@router.get("/meetings", response_model=list[MeetingResponse])
async def meetings(
    start: Annotated[datetime, Query()],
    end: Annotated[datetime, Query()],
    db: Db,
    user: CurrentUser,
    club_id: int | None = None,
) -> list[MeetingResponse]:
    start_utc, end_utc = utc_datetime(start), utc_datetime(end)
    if end_utc <= start_utc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid date range")
    results = await repository.list_meetings(db, user.id, start_utc, end_utc, club_id)
    return [meeting_response(item, user.id) for item in results]


@router.post("/meetings", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(data: MeetingCreate, db: Db, user: CurrentUser) -> MeetingResponse:
    await require_book_manager(db, data.club_id, user.id)
    return meeting_response(await repository.create_meeting(db, user.id, data), user.id)


@router.patch("/meetings/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int, data: MeetingUpdate, db: Db, user: CurrentUser
) -> MeetingResponse:
    meeting = await require_meeting(db, meeting_id)
    await require_book_manager(db, meeting.club_id, user.id)
    start = data.start_time or meeting.start_time
    end = data.end_time or meeting.end_time
    if start.tzinfo is None:
        start = start.replace(tzinfo=UTC)
    if end.tzinfo is None:
        end = end.replace(tzinfo=UTC)
    if end <= start:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "End time must be after start")
    return meeting_response(await repository.update_meeting(db, meeting, data), user.id)


@router.post("/meetings/{meeting_id}/cancel", response_model=MeetingResponse)
async def cancel_meeting(meeting_id: int, db: Db, user: CurrentUser) -> MeetingResponse:
    meeting = await require_meeting(db, meeting_id)
    await require_book_manager(db, meeting.club_id, user.id)
    return meeting_response(await repository.cancel_meeting(db, meeting), user.id)


@router.put("/meetings/{meeting_id}/rsvp", response_model=AttendeeResponse)
async def rsvp(meeting_id: int, data: RsvpUpdate, db: Db, user: CurrentUser) -> AttendeeResponse:
    meeting = await require_meeting(db, meeting_id)
    await require_participant(db, meeting.club_id, user.id)
    attendee: MeetingAttendee = await repository.set_rsvp(db, meeting_id, user.id, data.status)
    return AttendeeResponse.model_validate(attendee)


@router.get("/availability/me", response_model=list[AvailabilityResponse])
async def my_availability(
    db: Db,
    user: CurrentUser,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[AvailabilityResponse]:
    start_utc = utc_datetime(start) if start else None
    end_utc = utc_datetime(end) if end else None
    return [
        AvailabilityResponse.model_validate(item)
        for item in await repository.user_availability(db, user.id, start_utc, end_utc)
    ]


@router.put("/availability/me", response_model=list[AvailabilityResponse])
async def update_availability(
    data: AvailabilityUpdate, db: Db, user: CurrentUser
) -> list[AvailabilityResponse]:
    return [
        AvailabilityResponse.model_validate(item)
        for item in await repository.replace_availability(db, user.id, data.intervals)
    ]


@router.get("/availability/clubs/{club_id}", response_model=list[AvailabilityResponse])
async def availability_for_club(
    club_id: int,
    start: Annotated[datetime, Query()],
    end: Annotated[datetime, Query()],
    db: Db,
    user: CurrentUser,
) -> list[AvailabilityResponse]:
    await require_participant(db, club_id, user.id)
    start_utc, end_utc = utc_datetime(start), utc_datetime(end)
    return [
        AvailabilityResponse.model_validate(item)
        for item in await repository.club_availability(db, club_id, start_utc, end_utc)
    ]
