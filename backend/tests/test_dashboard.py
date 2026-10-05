from datetime import UTC, datetime, timedelta

from httpx import AsyncClient


async def test_dashboard_aggregates_user_workspace(client: AsyncClient) -> None:
    registration = await client.post(
        "/auth/register",
        json={
            "username": "dashboard_reader",
            "email": "dashboard@example.com",
            "password": "dashboard-password",
            "first_name": "Dashboard",
            "last_name": "Reader",
        },
    )
    token = registration.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = registration.json()["user"]["id"]
    book = {
        "open_library_key": "DASH1W",
        "title": "Dashboard Book",
        "author": "D. Writer",
        "genres": ["Mystery"],
    }
    await client.put(
        "/books/library",
        headers=headers,
        json={"book": book, "status": "READING"},
    )
    await client.put("/books/preferences", headers=headers, json={"genres": ["Mystery", "Fiction"]})
    club = await client.post(
        "/clubs",
        headers=headers,
        json={"name": "Dashboard Club", "is_public": True},
    )
    club_id = club.json()["id"]
    await client.put(
        f"/clubs/{club_id}/books",
        headers=headers,
        json={"book": book, "status": "CURRENT"},
    )
    start = datetime.now(UTC) + timedelta(days=2)
    await client.post(
        "/meetings",
        headers=headers,
        json={
            "club_id": club_id,
            "title": "Dashboard Meeting",
            "start_time": start.isoformat(),
            "end_time": (start + timedelta(hours=1)).isoformat(),
            "timezone": "UTC",
            "invitee_ids": [user_id],
        },
    )

    response = await client.get("/dashboard", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["currently_reading"][0]["book"]["title"] == "Dashboard Book"
    assert body["favorite_genres"] == ["Fiction", "Mystery"]
    assert body["clubs"][0]["current_book"]["title"] == "Dashboard Book"
    assert body["upcoming_meetings"][0]["title"] == "Dashboard Meeting"
