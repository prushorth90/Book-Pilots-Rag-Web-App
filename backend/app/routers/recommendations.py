from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import get_settings
from app.database.session import get_db
from app.models.user import User
from app.recommender import RecommendationEngine
from app.schemas.books import BookResponse
from app.schemas.recommendations import RecommendationResponse

router = APIRouter(tags=["recommendations"])


@lru_cache
def get_recommendation_engine() -> RecommendationEngine:
    settings = get_settings()
    return RecommendationEngine(settings.recommender_artifact_dir, settings.recommender_min_ratings)


@router.get("/recommendations", response_model=list[RecommendationResponse])
async def recommendations(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    engine: Annotated[RecommendationEngine, Depends(get_recommendation_engine)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[RecommendationResponse]:
    try:
        results = await engine.recommend(db, user.id, limit)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Recommendation artifacts are unavailable; run the training command",
        ) from error
    return [
        RecommendationResponse(
            book=BookResponse.model_validate(book), score=score, explanation=explanation
        )
        for book, score, explanation in results
    ]
