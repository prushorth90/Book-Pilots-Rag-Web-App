from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.book import ReadingStatus


class SearchField(str, Enum):
    KEYWORD = "keyword"
    TITLE = "title"
    AUTHOR = "author"
    ISBN = "isbn"


class BookData(BaseModel):
    open_library_key: str
    title: str
    author: str = "Unknown author"
    description: Optional[str] = None
    isbn: Optional[str] = None
    cover_image_url: Optional[str] = None
    publication_year: Optional[int] = None
    genres: list[str] = Field(default_factory=list)
    average_rating: Optional[float] = None


class BookResponse(BookData):
    id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    total: int
    books: list[BookData]


class LibraryUpdate(BaseModel):
    book: BookData
    status: ReadingStatus
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    review: Optional[str] = Field(default=None, max_length=5000)


class UserBookResponse(BaseModel):
    id: int
    status: ReadingStatus
    rating: Optional[int]
    review: Optional[str]
    book: BookResponse
    model_config = ConfigDict(from_attributes=True)


class GenrePreferences(BaseModel):
    genres: list[str] = Field(max_length=20)
