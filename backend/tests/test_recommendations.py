from pathlib import Path

from httpx import AsyncClient
from sqlalchemy import select

from app.database.session import get_db
from app.models.book import Book
from app.recommender.feature_preparation import prepare_content_features, save_content_artifacts
from app.recommender.inference import RecommendationEngine
from app.routers.recommendations import get_recommendation_engine

USER = {
    "username": "recommend_reader",
    "email": "recommend@example.com",
    "password": "recommend-reader-password",
    "first_name": "Recommendation",
    "last_name": "Reader",
}


async def test_cold_start_recommendations_use_genre_preferences(
    client: AsyncClient, tmp_path: Path
) -> None:
    registration = await client.post("/auth/register", json=USER)
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    await client.put("/books/preferences", headers=headers, json={"genres": ["Fantasy"]})

    override = client._transport.app.dependency_overrides[get_db]  # type: ignore[attr-defined]
    database = override()
    session = await anext(database)
    fantasy = Book(
        open_library_key="FANTASY1",
        title="Dragons of Dawn",
        author="F. Author",
        description="A magical dragon adventure",
        genres=["Fantasy"],
    )
    history = Book(
        open_library_key="HISTORY1",
        title="A History of Ports",
        author="H. Author",
        description="Trade routes and harbors",
        genres=["History"],
    )
    session.add_all([fantasy, history])
    await session.commit()
    books = list((await session.execute(select(Book).order_by(Book.id))).scalars().all())
    save_content_artifacts(prepare_content_features(books), tmp_path)
    await database.aclose()

    client._transport.app.dependency_overrides[get_recommendation_engine] = (
        lambda: RecommendationEngine(  # type: ignore[attr-defined]
            tmp_path
        )
    )
    response = await client.get("/recommendations", headers=headers)

    assert response.status_code == 200
    assert response.json()[0]["book"]["title"] == "Dragons of Dawn"
    assert response.json()[0]["score"] > response.json()[1]["score"]
    assert "fantasy" in response.json()[0]["explanation"].lower()


async def test_recommendations_require_authentication(client: AsyncClient) -> None:
    assert (await client.get("/recommendations")).status_code == 401
