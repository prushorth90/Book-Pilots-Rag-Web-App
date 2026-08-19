from datetime import UTC, datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from app.models.meeting import MeetingStatus, RsvpStatus
from app.schemas.auth import UserResponse


def utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Datetime must include a timezone offset")
    return value.astimezone(UTC)


class TimeRange(BaseModel):
    start_time: datetime
    end_time: datetime

    @field_validator("start_time", "end_time")
    @classmethod
    def normalize_time(cls, value: datetime) -> datetime:
        return utc_datetime(value)

    @model_validator(mode="after")
    def valid_range(self) -> "TimeRange":
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self


class MeetingCreate(TimeRange):
    club_id: int
    title: str = Field(min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    timezone: str = Field(min_length=1, max_length=100)
    location: Optional[str] = Field(default=None, max_length=1000)


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    timezone: Optional[str] = Field(default=None, min_length=1, max_length=100)
    location: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("start_time", "end_time")
    @classmethod
    def normalize_optional_time(cls, value: Optional[datetime]) -> Optional[datetime]:
        return utc_datetime(value) if value else None


class RsvpUpdate(BaseModel):
    status: RsvpStatus


class AttendeeResponse(BaseModel):
    id: int
    status: RsvpStatus
    user: UserResponse
    model_config = ConfigDict(from_attributes=True)


class MeetingResponse(BaseModel):
    id: int
    club_id: int
    club_name: str
    creator_id: int
    organizer: UserResponse
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    timezone: str
    location: Optional[str]
    status: MeetingStatus
    created_at: datetime
    attendees: list[AttendeeResponse]
    viewer_rsvp: Optional[RsvpStatus] = None

    @field_serializer("start_time", "end_time", "created_at")
    def serialize_utc(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


class AvailabilityInput(TimeRange):
    timezone: str = Field(min_length=1, max_length=100)


class AvailabilityUpdate(BaseModel):
    intervals: list[AvailabilityInput] = Field(max_length=100)


class AvailabilityResponse(BaseModel):
    id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    timezone: str
    user: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("start_time", "end_time")
    def serialize_utc(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
