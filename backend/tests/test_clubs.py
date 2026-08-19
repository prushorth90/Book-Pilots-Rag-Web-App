from httpx import AsyncClient


async def register(client: AsyncClient, username: str) -> tuple[dict[str, str], int]:
    response = await client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "club-test-password",
            "first_name": username,
            "last_name": "Reader",
        },
    )
    body = response.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body["user"]["id"]


async def test_club_membership_roles_and_book_permissions(client: AsyncClient) -> None:
    owner_headers, _ = await register(client, "club_owner")
    member_headers, _ = await register(client, "club_member")
    club = await client.post(
        "/clubs",
        headers=owner_headers,
        json={"name": "Test Readers", "description": "A test club", "is_public": True},
    )
    club_id = club.json()["id"]
    joined = await client.post(f"/clubs/{club_id}/join", headers=member_headers)
    member_id = joined.json()["id"]

    forbidden_edit = await client.patch(
        f"/clubs/{club_id}", headers=member_headers, json={"description": "Nope"}
    )
    promoted = await client.patch(
        f"/clubs/{club_id}/members/{member_id}",
        headers=owner_headers,
        json={"role": "ADMIN"},
    )
    book = {
        "open_library_key": "CLUB1W",
        "title": "The Club Book",
        "author": "A. Writer",
        "description": None,
        "isbn": None,
        "cover_image_url": None,
        "publication_year": 2025,
        "genres": ["Fiction"],
        "average_rating": 4.2,
    }
    saved_book = await client.put(
        f"/clubs/{club_id}/books",
        headers=member_headers,
        json={"book": book, "status": "CURRENT"},
    )
    detail = await client.get(f"/clubs/{club_id}", headers=member_headers)

    assert club.status_code == 201
    assert club.json()["viewer_role"] == "OWNER"
    assert joined.json()["role"] == "MEMBER"
    assert forbidden_edit.status_code == 403
    assert promoted.json()["role"] == "ADMIN"
    assert saved_book.status_code == 200
    assert detail.json()["current_book"]["title"] == "The Club Book"
    assert len(detail.json()["members"]) == 2


async def test_owner_cannot_leave_and_member_can_leave(client: AsyncClient) -> None:
    owner_headers, _ = await register(client, "leave_owner")
    member_headers, _ = await register(client, "leave_member")
    club = await client.post(
        "/clubs", headers=owner_headers, json={"name": "Leaving Club", "is_public": True}
    )
    club_id = club.json()["id"]
    await client.post(f"/clubs/{club_id}/join", headers=member_headers)

    assert (
        await client.delete(f"/clubs/{club_id}/leave", headers=owner_headers)
    ).status_code == 409
    assert (
        await client.delete(f"/clubs/{club_id}/leave", headers=member_headers)
    ).status_code == 204
