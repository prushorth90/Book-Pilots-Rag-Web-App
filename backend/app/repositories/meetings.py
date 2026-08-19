from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.club import BookClubMember
from app.models.meeting import (
    Meeting,
    MeetingAttendee,
    MeetingStatus,
    RsvpStatus,
    UserAvailability,
    WeeklyAvailability,
)
from app.models.user import User
from app.schemas.meetings import (
    AvailabilityInput,
    MeetingCreate,
    MeetingUpdate,
    SuggestedSlot,
    WeeklyAvailabilityInput,
)


async def get_meeting(db: AsyncSession, meeting_id: int) -> Meeting | None:
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.unique().scalar_one_or_none()


async def list_meetings(
    db: AsyncSession,
    user_id: int,
    start: datetime,
    end: datetime,
    club_id: int | None,
    mine: bool,
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
    if mine:
        query = query.join(
            MeetingAttendee,
            (MeetingAttendee.meeting_id == Meeting.id) & (MeetingAttendee.user_id == user_id),
        ).where(MeetingAttendee.status != RsvpStatus.DECLINED)
    result = await db.execute(query)
    return list(result.unique().scalars())


async def create_meeting(db: AsyncSession, user_id: int, data: MeetingCreate) -> Meeting:
    values = data.model_dump(exclude={"invitee_ids"})
    meeting = Meeting(creator_id=user_id, status=MeetingStatus.SCHEDULED, **values)
    db.add(meeting)
    await db.flush()
    invitees = set(data.invitee_ids)
    invitees.add(user_id)
    db.add_all(
        MeetingAttendee(
            meeting_id=meeting.id,
            user_id=invitee_id,
            status=RsvpStatus.ACCEPTED if invitee_id == user_id else RsvpStatus.PENDING,
        )
        for invitee_id in invitees
    )
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


async def replace_weekly_availability(
    db: AsyncSession, user_id: int, rules: list[WeeklyAvailabilityInput]
) -> list[WeeklyAvailability]:
    await db.execute(delete(WeeklyAvailability).where(WeeklyAvailability.user_id == user_id))
    db.add_all(WeeklyAvailability(user_id=user_id, **rule.model_dump()) for rule in rules)
    await db.commit()
    return await weekly_availability(db, user_id)


async def weekly_availability(db: AsyncSession, user_id: int) -> list[WeeklyAvailability]:
    result = await db.execute(
        select(WeeklyAvailability)
        .where(WeeklyAvailability.user_id == user_id)
        .order_by(WeeklyAvailability.weekday, WeeklyAvailability.start_minute)
    )
    return list(result.scalars())


async def meeting_conflicts(
    db: AsyncSession,
    user_ids: set[int],
    start: datetime,
    end: datetime,
    exclude_meeting_id: int | None = None,
) -> list[tuple[Meeting, User]]:
    if not user_ids:
        return []
    query = (
        select(Meeting, User)
        .join(MeetingAttendee, MeetingAttendee.meeting_id == Meeting.id)
        .join(User, User.id == MeetingAttendee.user_id)
        .where(
            MeetingAttendee.user_id.in_(user_ids),
            MeetingAttendee.status != RsvpStatus.DECLINED,
            Meeting.status == MeetingStatus.SCHEDULED,
            Meeting.start_time < end,
            Meeting.end_time > start,
        )
    )
    if exclude_meeting_id is not None:
        query = query.where(Meeting.id != exclude_meeting_id)
    rows = (await db.execute(query)).unique().all()
    return [(row[0], row[1]) for row in rows]


async def suggested_slots(
    db: AsyncSession,
    user_ids: set[int],
    start: datetime,
    end: datetime,
    duration_minutes: int,
) -> list[SuggestedSlot]:
    if not user_ids:
        return []
    rules = list(
        (
            await db.execute(
                select(WeeklyAvailability).where(WeeklyAvailability.user_id.in_(user_ids))
            )
        ).scalars()
    )
    by_user: dict[int, list[tuple[datetime, datetime]]] = {user_id: [] for user_id in user_ids}
    current_date: date = start.date() - timedelta(days=1)
    final_date = end.date() + timedelta(days=1)
    while current_date <= final_date:
        for rule in rules:
            if current_date.weekday() != rule.weekday:
                continue
            try:
                zone = ZoneInfo(rule.timezone)
            except ZoneInfoNotFoundError:
                continue
            midnight = datetime.combine(current_date, time.min, tzinfo=zone)
            slot_start = (midnight + timedelta(minutes=rule.start_minute)).astimezone(UTC)
            slot_end = (midnight + timedelta(minutes=rule.end_minute)).astimezone(UTC)
            if slot_start < end and slot_end > start:
                by_user[rule.user_id].append((max(slot_start, start), min(slot_end, end)))
        current_date += timedelta(days=1)

    candidates: list[SuggestedSlot] = []
    duration = timedelta(minutes=duration_minutes)
    for anchor_user, intervals in by_user.items():
        del anchor_user
        for interval_start, interval_end in intervals:
            cursor = interval_start.replace(
                minute=(interval_start.minute // 30) * 30, second=0, microsecond=0
            )
            if cursor < interval_start:
                cursor += timedelta(minutes=30)
            while cursor + duration <= interval_end:
                candidate_end = cursor + duration
                available = sorted(
                    user_id
                    for user_id, user_intervals in by_user.items()
                    if any(
                        begin <= cursor and finish >= candidate_end
                        for begin, finish in user_intervals
                    )
                )
                if set(available) == user_ids and not await meeting_conflicts(
                    db, user_ids, cursor, candidate_end
                ):
                    candidates.append(
                        SuggestedSlot(
                            start_time=cursor,
                            end_time=candidate_end,
                            available_user_ids=available,
                        )
                    )
                cursor += timedelta(minutes=30)
    unique = {(item.start_time, item.end_time): item for item in candidates}
    return sorted(unique.values(), key=lambda item: item.start_time)[:20]


async def required_meeting(db: AsyncSession, meeting_id: int) -> Meeting:
    meeting = await get_meeting(db, meeting_id)
    if meeting is None:
        raise RuntimeError("Meeting disappeared after persistence")
    return meeting
