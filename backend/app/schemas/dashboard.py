from pydantic import BaseModel

from app.models.club import ClubRole
from app.schemas.books import BookResponse, UserBookResponse
from app.schemas.communication import MessageResponse
from app.schemas.meetings import MeetingResponse
from app.schemas.recommendations import RecommendationResponse


class DashboardClub(BaseModel):
    id: int
    name: str
    role: ClubRole
    member_count: int
    current_book: BookResponse | None = None


class DashboardMessage(BaseModel):
    club_name: str
    message: MessageResponse


class DashboardResponse(BaseModel):
    currently_reading: list[UserBookResponse]
    want_to_read: list[UserBookResponse]
    recommendations: list[RecommendationResponse]
    favorite_genres: list[str]
    clubs: list[DashboardClub]
    recent_messages: list[DashboardMessage]
    upcoming_meetings: list[MeetingResponse]
