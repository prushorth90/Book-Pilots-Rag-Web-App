from httpx import AsyncClient


async def register(client: AsyncClient, username: str) -> dict[str, str]:
    response = await client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "meeting-test-password",
            "first_name": username,
            "last_name": "Reader",
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_meeting_utc_authorization_rsvp_and_cancel(client: AsyncClient) -> None:
    owner = await register(client, "meeting_owner")
    member = await register(client, "meeting_member")
    club = await client.post(
        "/clubs", headers=owner, json={"name": "Calendar Club", "is_public": True}
    )
    club_id = club.json()["id"]
    await client.post(f"/clubs/{club_id}/join", headers=member)
    data = {
        "club_id": club_id,
        "title": "Evening discussion",
        "description": "Discuss the current chapters",
        "start_time": "2026-08-20T19:00:00-04:00",
        "end_time": "2026-08-20T20:30:00-04:00",
        "timezone": "America/New_York",
        "location": "https://meet.example.com/readers",
    }
    forbidden = await client.post("/meetings", headers=member, json=data)
    created = await client.post("/meetings", headers=owner, json=data)
    meeting_id = created.json()["id"]
    listed = await client.get(
        "/meetings?start=2026-08-20T00:00:00Z&end=2026-08-22T00:00:00Z",
        headers=member,
    )
    rsvp = await client.put(
        f"/meetings/{meeting_id}/rsvp", headers=member, json={"status": "GOING"}
    )
    cancelled = await client.post(f"/meetings/{meeting_id}/cancel", headers=owner)

    assert forbidden.status_code == 403
    assert created.status_code == 201
    assert created.json()["start_time"] == "2026-08-20T23:00:00Z"
    assert listed.json()[0]["club_name"] == "Calendar Club"
    assert rsvp.json()["status"] == "ACCEPTED"
    assert cancelled.json()["status"] == "CANCELLED"


async def test_user_and_club_availability(client: AsyncClient) -> None:
    owner = await register(client, "availability_owner")
    club = await client.post(
        "/clubs", headers=owner, json={"name": "Available Club", "is_public": True}
    )
    payload = {
        "intervals": [
            {
                "start_time": "2026-08-21T18:00:00+02:00",
                "end_time": "2026-08-21T20:00:00+02:00",
                "timezone": "Europe/Paris",
            }
        ]
    }
    saved = await client.put("/availability/me", headers=owner, json=payload)
    club_slots = await client.get(
        f"/availability/clubs/{club.json()['id']}?start=2026-08-21T00:00:00Z&end=2026-08-22T00:00:00Z",
        headers=owner,
    )

    assert saved.status_code == 200
    assert saved.json()[0]["start_time"] == "2026-08-21T16:00:00Z"
    assert len(club_slots.json()) == 1


async def test_weekly_overlap_suggestions_timezone_and_conflicts(client: AsyncClient) -> None:
    owner = await register(client, "suggestion_owner")
    member = await register(client, "suggestion_member")
    club = await client.post(
        "/clubs", headers=owner, json={"name": "Suggestion Club", "is_public": True}
    )
    club_id = club.json()["id"]
    joined = await client.post(f"/clubs/{club_id}/join", headers=member)
    owner_user = (await client.get("/auth/me", headers=owner)).json()
    member_id = joined.json()["user"]["id"]

    owner_rules = {
        "rules": [
            {
                "weekday": 0,
                "start_minute": 18 * 60,
                "end_minute": 21 * 60,
                "timezone": "America/New_York",
            }
        ]
    }
    member_rules = {
        "rules": [
            {
                "weekday": 0,
                "start_minute": 19 * 60,
                "end_minute": 22 * 60,
                "timezone": "America/New_York",
            }
        ]
    }
    assert (
        await client.put("/availability/weekly", headers=owner, json=owner_rules)
    ).status_code == 200
    assert (
        await client.put("/availability/weekly", headers=member, json=member_rules)
    ).status_code == 200

    suggestions = await client.get(
        "/meetings/suggestions",
        headers=owner,
        params={
            "club_id": club_id,
            "start": "2026-08-24T00:00:00Z",
            "end": "2026-08-25T23:59:00Z",
            "duration_minutes": 60,
            "invitee_ids": member_id,
        },
    )
    first = suggestions.json()[0]
    assert first["start_time"] == "2026-08-24T23:00:00Z"
    assert first["available_user_ids"] == sorted([owner_user["id"], member_id])

    meeting = {
        "club_id": club_id,
        "title": "Suggested meeting",
        "start_time": first["start_time"],
        "end_time": first["end_time"],
        "timezone": "America/New_York",
        "invitee_ids": [member_id],
    }
    created = await client.post("/meetings", headers=owner, json=meeting)
    conflict = await client.post(
        "/meetings", headers=owner, json={**meeting, "title": "Conflicting meeting"}
    )
    mine = await client.get(
        "/meetings",
        headers=member,
        params={
            "start": "2026-08-24T00:00:00Z",
            "end": "2026-08-25T23:59:00Z",
            "mine": True,
        },
    )

    assert created.status_code == 201
    assert created.json()["attendees"][1]["status"] == "PENDING"
    assert conflict.status_code == 409
    assert "Scheduling conflict" in conflict.json()["detail"]
    assert len(mine.json()) == 1


async def test_new_rsvp_states(client: AsyncClient) -> None:
    owner = await register(client, "rsvp_owner")
    member = await register(client, "rsvp_member")
    club = await client.post("/clubs", headers=owner, json={"name": "RSVP Club", "is_public": True})
    club_id = club.json()["id"]
    joined = await client.post(f"/clubs/{club_id}/join", headers=member)
    meeting = await client.post(
        "/meetings",
        headers=owner,
        json={
            "club_id": club_id,
            "title": "RSVP meeting",
            "start_time": "2026-09-01T18:00:00Z",
            "end_time": "2026-09-01T19:00:00Z",
            "timezone": "UTC",
            "invitee_ids": [joined.json()["user"]["id"]],
        },
    )
    meeting_id = meeting.json()["id"]
    for rsvp_status in ["ACCEPTED", "MAYBE", "DECLINED"]:
        response = await client.put(
            f"/meetings/{meeting_id}/rsvp",
            headers=member,
            json={"status": rsvp_status},
        )
        assert response.json()["status"] == rsvp_status
