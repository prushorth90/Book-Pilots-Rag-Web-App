from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.club import BookClubMember
from app.models.meeting import Meeting, MeetingAttendee, MeetingStatus, RsvpStatus, UserAvailability
from app.schemas.meetings import AvailabilityInput, MeetingCreate, MeetingUpdate


async def get_meeting(db: AsyncSession, meeting_id: int) -> Meeting | None:
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.unique().scalar_one_or_none()


async def list_meetings(
    db: AsyncSession, user_id: int, start: datetime, end: datetime, club_id: int | None
) -> list[Meeting]:
    query = (
        select(Meeting)
        .join(BookClubMember, BookClubMember.club_id == Meeting.club_id)
        .where(
            BookClubMember.user_id == user_id,
            Meeting.start_time < end,
            Meeting.end_time > start,
        )
        .order_by(Meeting.start_time)
    )
    if club_id is not None:
        query = query.where(Meeting.club_id == club_id)
    result = await db.execute(query)
    return list(result.unique().scalars())


async def create_meeting(db: AsyncSession, user_id: int, data: MeetingCreate) -> Meeting:
    meeting = Meeting(creator_id=user_id, status=MeetingStatus.SCHEDULED, **data.model_dump())
    db.add(meeting)
    await db.flush()
    db.add(MeetingAttendee(meeting_id=meeting.id, user_id=user_id, status=RsvpStatus.GOING))
    await db.commit()
    return await required_meeting(db, meeting.id)


async def update_meeting(db: AsyncSession, meeting: Meeting, data: MeetingUpdate) -> Meeting:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)
    await db.commit()
    return await required_meeting(db, meeting.id)


async def cancel_meeting(db: AsyncSession, meeting: Meeting) -> Meeting:
    meeting.status = MeetingStatus.CANCELLED
    await db.commit()
    return await required_meeting(db, meeting.id)


async def set_rsvp(
    db: AsyncSession, meeting_id: int, user_id: int, status: RsvpStatus
) -> MeetingAttendee:
    result = await db.execute(
        select(MeetingAttendee).where(
            MeetingAttendee.meeting_id == meeting_id, MeetingAttendee.user_id == user_id
        )
    )
    attendee = result.scalar_one_or_none()
    if attendee:
        attendee.status = status
    else:
        attendee = MeetingAttendee(meeting_id=meeting_id, user_id=user_id, status=status)
        db.add(attendee)
    await db.commit()
    await db.refresh(attendee)
    return attendee


async def replace_availability(
    db: AsyncSession, user_id: int, intervals: list[AvailabilityInput]
) -> list[UserAvailability]:
    await db.execute(delete(UserAvailability).where(UserAvailability.user_id == user_id))
    db.add_all(UserAvailability(user_id=user_id, **interval.model_dump()) for interval in intervals)
    await db.commit()
    return await user_availability(db, user_id, None, None)


async def user_availability(
    db: AsyncSession, user_id: int, start: datetime | None, end: datetime | None
) -> list[UserAvailability]:
    query = select(UserAvailability).where(UserAvailability.user_id == user_id)
    if start and end:
        query = query.where(UserAvailability.start_time < end, UserAvailability.end_time > start)
    result = await db.execute(query.order_by(UserAvailability.start_time))
    return list(result.scalars())


async def club_availability(
    db: AsyncSession, club_id: int, start: datetime, end: datetime
) -> list[UserAvailability]:
    result = await db.execute(
        select(UserAvailability)
        .join(BookClubMember, BookClubMember.user_id == UserAvailability.user_id)
        .where(
            BookClubMember.club_id == club_id,
            UserAvailability.start_time < end,
            UserAvailability.end_time > start,
        )
        .order_by(UserAvailability.start_time)
    )
    return list(result.scalars())


async def required_meeting(db: AsyncSession, meeting_id: int) -> Meeting:
    meeting = await get_meeting(db, meeting_id)
    if meeting is None:
        raise RuntimeError("Meeting disappeared after persistence")
    return meeting
