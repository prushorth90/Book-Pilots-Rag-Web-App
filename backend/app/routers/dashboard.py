from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database.session import get_db
from app.models.book import ReadingStatus
from app.models.user import User
from app.recommender import RecommendationEngine
from app.repositories import dashboard as repository
from app.repositories.meetings import list_meetings
from app.routers.meetings import meeting_response
from app.routers.recommendations import get_recommendation_engine
from app.schemas.books import BookResponse, UserBookResponse
from app.schemas.communication import MessageResponse
from app.schemas.dashboard import DashboardClub, DashboardMessage, DashboardResponse
from app.schemas.recommendations import RecommendationResponse

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    engine: Annotated[RecommendationEngine, Depends(get_recommendation_engine)],
) -> DashboardResponse:
    library, genres = await repository.reading_and_genres(db, user.id)
    club_rows = await repository.club_overview(db, user.id)
    club_ids = [club.id for _, club, _, _ in club_rows]
    messages = await repository.recent_messages(db, club_ids)
    now = datetime.now(UTC)
    meetings = await list_meetings(db, user.id, now, now + timedelta(days=30), None, True)
    try:
        recommendations = await engine.recommend(db, user.id, 6)
    except (FileNotFoundError, ValueError):
        recommendations = []

    return DashboardResponse(
        currently_reading=[
            UserBookResponse.model_validate(entry)
            for entry in library
            if entry.status == ReadingStatus.READING
        ],
        want_to_read=[
            UserBookResponse.model_validate(entry)
            for entry in library
            if entry.status == ReadingStatus.WANT_TO_READ
        ],
        recommendations=[
            RecommendationResponse(
                book=BookResponse.model_validate(book),
                score=score,
                explanation=explanation,
            )
            for book, score, explanation in recommendations
        ],
        favorite_genres=genres,
        clubs=[
            DashboardClub(
                id=club.id,
                name=club.name,
                role=membership.role,
                member_count=count,
                current_book=(BookResponse.model_validate(club_book.book) if club_book else None),
            )
            for membership, club, club_book, count in club_rows
        ],
        recent_messages=[
            DashboardMessage(
                club_name=next(
                    club.name for _, club, _, _ in club_rows if club.id == message.club_id
                ),
                message=MessageResponse.model_validate(message),
            )
            for message in messages
        ],
        upcoming_meetings=[
            meeting_response(meeting, user.id)
            for meeting in meetings
            if meeting.status.value == "SCHEDULED"
        ][:6],
    )
