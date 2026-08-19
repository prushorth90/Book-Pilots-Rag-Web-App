from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.club import ClubBookStatus, ClubRole
from app.schemas.auth import UserResponse
from app.schemas.books import BookData, BookResponse


class ClubCreate(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: Optional[str] = Field(default=None, max_length=5000)
    is_public: bool = True


class ClubUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=150)
    description: Optional[str] = Field(default=None, max_length=5000)
    is_public: Optional[bool] = None


class ClubSummary(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    member_count: int = 0
    current_book: Optional[BookResponse] = None
    model_config = ConfigDict(from_attributes=True)


class ClubMemberResponse(BaseModel):
    id: int
    role: ClubRole
    joined_at: datetime
    user: UserResponse
    model_config = ConfigDict(from_attributes=True)


class ClubBookResponse(BaseModel):
    id: int
    status: ClubBookStatus
    book: BookResponse
    model_config = ConfigDict(from_attributes=True)


class ClubDetail(ClubSummary):
    members: list[ClubMemberResponse]
    books: list[ClubBookResponse]
    viewer_role: Optional[ClubRole] = None


class RoleUpdate(BaseModel):
    role: ClubRole


class ClubBookUpdate(BaseModel):
    book: BookData
    status: ClubBookStatus
