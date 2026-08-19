from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.books import (
    delete_library_entry,
    get_genres,
    list_library,
    save_library_entry,
    set_genres,
)
from app.schemas.books import (
    BookData,
    GenrePreferences,
    LibraryUpdate,
    SearchField,
    SearchResponse,
    UserBookResponse,
)
from app.services.open_library import get_book_details, search_books

router = APIRouter(prefix="/books", tags=["books"])
Db = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/search", response_model=SearchResponse)
async def search(
    user: CurrentUser,
    query: Annotated[str, Query(min_length=1, max_length=200)],
    field: SearchField = SearchField.KEYWORD,
    page: Annotated[int, Query(ge=1)] = 1,
) -> SearchResponse:
    del user
    try:
        return await search_books(query, field, page)
    except httpx.HTTPError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Open Library is unavailable") from error


@router.get("/details/{work_id}", response_model=BookData)
async def details(work_id: str, user: CurrentUser) -> BookData:
    del user
    try:
        return await get_book_details(work_id)
    except httpx.HTTPError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Open Library is unavailable") from error


@router.get("/library", response_model=list[UserBookResponse])
async def library(db: Db, user: CurrentUser) -> list[UserBookResponse]:
    entries = await list_library(db, user.id)
    return [UserBookResponse.model_validate(entry) for entry in entries]


@router.put("/library", response_model=UserBookResponse)
async def update_library(data: LibraryUpdate, db: Db, user: CurrentUser) -> UserBookResponse:
    return UserBookResponse.model_validate(await save_library_entry(db, user.id, data))


@router.delete("/library/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_library(work_id: str, db: Db, user: CurrentUser) -> Response:
    await delete_library_entry(db, user.id, work_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/preferences", response_model=GenrePreferences)
async def preferences(db: Db, user: CurrentUser) -> GenrePreferences:
    return GenrePreferences(genres=await get_genres(db, user.id))


@router.put("/preferences", response_model=GenrePreferences)
async def update_preferences(data: GenrePreferences, db: Db, user: CurrentUser) -> GenrePreferences:
    return GenrePreferences(genres=await set_genres(db, user.id, data.genres))
