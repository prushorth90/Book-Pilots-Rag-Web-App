from pydantic import BaseModel

from app.schemas.books import BookResponse


class RecommendationResponse(BaseModel):
    book: BookResponse
    score: float
    explanation: str
