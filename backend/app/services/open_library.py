from __future__ import annotations

from typing import Any

import httpx

from app.schemas.books import BookData, SearchField, SearchResponse

SEARCH_URL = "https://openlibrary.org/search.json"
FIELDS = (
    "key,title,author_name,first_publish_year,isbn,cover_i,subject,ratings_average,first_sentence"
)


def _text(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        text = value.get("value")
        return text if isinstance(text, str) else None
    if isinstance(value, list) and value and isinstance(value[0], str):
        return value[0]
    return None


def normalize_book(document: dict[str, Any]) -> BookData:
    raw_key = str(document.get("key") or "")
    key = raw_key.removeprefix("/works/") or "unknown"
    authors = document.get("author_name")
    author = ", ".join(str(name) for name in authors if name) if isinstance(authors, list) else ""
    isbns = document.get("isbn")
    isbn = str(isbns[0]) if isinstance(isbns, list) and isbns else None
    cover_id = document.get("cover_i") or document.get("covers", [None])[0]
    subjects = document.get("subject") or document.get("subjects") or []
    genres = [str(item) for item in subjects[:8]] if isinstance(subjects, list) else []
    year = document.get("first_publish_year")
    rating = document.get("ratings_average")
    return BookData(
        open_library_key=key,
        title=str(document.get("title") or "Untitled"),
        author=author or "Unknown author",
        description=_text(document.get("description")) or _text(document.get("first_sentence")),
        isbn=isbn,
        cover_image_url=(
            f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None
        ),
        publication_year=int(year) if isinstance(year, (int, float)) else None,
        genres=genres,
        average_rating=round(float(rating), 2) if isinstance(rating, (int, float)) else None,
    )


async def search_books(query: str, field: SearchField, page: int = 1) -> SearchResponse:
    parameter = "q" if field == SearchField.KEYWORD else field.value
    async with httpx.AsyncClient(timeout=12, headers={"User-Agent": "BookPilots/1.0"}) as client:
        response = await client.get(
            SEARCH_URL,
            params={parameter: query, "page": page, "limit": 20, "fields": FIELDS},
        )
        response.raise_for_status()
    payload = response.json()
    return SearchResponse(
        total=int(payload.get("numFound", payload.get("num_found", 0))),
        books=[normalize_book(document) for document in payload.get("docs", [])],
    )


async def get_book_details(work_id: str) -> BookData:
    async with httpx.AsyncClient(timeout=12, headers={"User-Agent": "BookPilots/1.0"}) as client:
        response = await client.get(f"https://openlibrary.org/works/{work_id}.json")
        response.raise_for_status()
    payload = response.json()
    payload["key"] = work_id
    return normalize_book(payload)
