from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.schemas.auth import UserResponse
from app.schemas.books import BookResponse


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: int
    club_id: int
    sender_id: int
    sender: UserResponse
    content: str
    is_deleted: bool
    created_at: datetime
    edited_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "edited_at")
    def serialize_time(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


class ThreadCreate(BaseModel):
    title: str = Field(min_length=2, max_length=250)


class PostCreate(MessageCreate):
    parent_id: Optional[int] = None


class PostResponse(BaseModel):
    id: int
    thread_id: int
    author_id: int
    author: UserResponse
    parent_id: Optional[int]
    content: str
    is_deleted: bool
    created_at: datetime
    edited_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class ThreadResponse(BaseModel):
    id: int
    club_id: int
    book_id: int
    creator_id: int
    creator: UserResponse
    book: BookResponse
    title: str
    created_at: datetime
    posts: list[PostResponse]
    model_config = ConfigDict(from_attributes=True)
