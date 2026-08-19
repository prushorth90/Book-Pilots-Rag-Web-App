from httpx import AsyncClient

from app.services.open_library import normalize_book

USER = {
    "username": "book_reader",
    "email": "books@example.com",
    "password": "book-reader-password",
    "first_name": "Book",
    "last_name": "Reader",
}
BOOK = {
    "open_library_key": "OL123W",
    "title": "A Test Book",
    "author": "A. Writer",
    "description": None,
    "isbn": None,
    "cover_image_url": None,
    "publication_year": None,
    "genres": ["Fantasy", "Adventure"],
    "average_rating": 4.25,
}


async def auth_headers(client: AsyncClient) -> dict[str, str]:
    response = await client.post("/auth/register", json=USER)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_open_library_normalization_handles_missing_fields() -> None:
    book = normalize_book({"key": "/works/OL1W", "title": "Sparse Book"})
    assert book.open_library_key == "OL1W"
    assert book.author == "Unknown author"
    assert book.description is None
    assert book.isbn is None
    assert book.cover_image_url is None
    assert book.genres == []


async def test_library_history_and_preferences_are_persisted(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    saved = await client.put(
        "/books/library",
        headers=headers,
        json={"book": BOOK, "status": "READ", "rating": 5, "review": "Excellent."},
    )
    library = await client.get("/books/library", headers=headers)
    preferences = await client.put(
        "/books/preferences", headers=headers, json={"genres": ["Fantasy", "Mystery", "Fantasy"]}
    )

    assert saved.status_code == 200
    assert saved.json()["rating"] == 5
    assert library.json()[0]["book"]["open_library_key"] == "OL123W"
    assert preferences.json() == {"genres": ["Fantasy", "Mystery"]}


async def test_library_requires_authentication(client: AsyncClient) -> None:
    assert (await client.get("/books/library")).status_code == 401
