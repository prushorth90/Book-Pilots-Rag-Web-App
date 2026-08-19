from httpx import AsyncClient


async def register(client: AsyncClient, username: str) -> tuple[dict[str, str], int]:
    response = await client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "communication-password",
            "first_name": username,
            "last_name": "Reader",
        },
    )
    body = response.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body["user"]["id"]


async def test_message_history_edit_delete_and_moderation(client: AsyncClient) -> None:
    owner, _ = await register(client, "chat_owner")
    member, _ = await register(client, "chat_member")
    club = await client.post("/clubs", headers=owner, json={"name": "Chat Club", "is_public": True})
    club_id = club.json()["id"]
    await client.post(f"/clubs/{club_id}/join", headers=member)

    from app.database.session import get_db
    from app.repositories.communication import create_message

    override = client._transport.app.dependency_overrides[get_db]  # type: ignore[attr-defined]
    generator = override()
    db = await anext(generator)
    message = await create_message(db, club_id, 2, "First persisted message")
    await generator.aclose()

    history = await client.get(f"/clubs/{club_id}/messages", headers=member)
    edited = await client.patch(
        f"/clubs/{club_id}/messages/{message.id}",
        headers=member,
        json={"content": "Edited message"},
    )
    forbidden = await client.delete(f"/clubs/{club_id}/messages/{message.id}", headers=owner)
    moderated = await client.post(
        f"/clubs/{club_id}/moderation/messages/{message.id}", headers=owner
    )

    assert history.json()[0]["content"] == "First persisted message"
    assert edited.json()["content"] == "Edited message"
    assert forbidden.status_code == 403
    assert moderated.json()["is_deleted"] is True


async def test_current_book_thread_and_replies(client: AsyncClient) -> None:
    owner, _ = await register(client, "discussion_owner")
    club = await client.post(
        "/clubs", headers=owner, json={"name": "Discussion Club", "is_public": True}
    )
    club_id = club.json()["id"]
    book = {
        "open_library_key": "DISCUSS1W",
        "title": "The Discussion Book",
        "author": "D. Writer",
        "genres": ["Fiction"],
    }
    await client.put(
        f"/clubs/{club_id}/books",
        headers=owner,
        json={"book": book, "status": "CURRENT"},
    )
    thread = await client.post(
        f"/clubs/{club_id}/discussions",
        headers=owner,
        json={"title": "Opening chapters"},
    )
    first = await client.post(
        f"/clubs/{club_id}/discussions/{thread.json()['id']}/posts",
        headers=owner,
        json={"content": "What did you notice?"},
    )
    reply = await client.post(
        f"/clubs/{club_id}/discussions/{thread.json()['id']}/posts",
        headers=owner,
        json={"content": "The narrator stood out.", "parent_id": first.json()["id"]},
    )
    threads = await client.get(f"/clubs/{club_id}/discussions", headers=owner)

    assert reply.json()["parent_id"] == first.json()["id"]
    assert threads.json()[0]["book"]["title"] == "The Discussion Book"
    assert len(threads.json()[0]["posts"]) == 2
