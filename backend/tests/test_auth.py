from httpx import AsyncClient

USER_DATA = {
    "username": "reader_one",
    "email": "reader@example.com",
    "password": "correct-horse-battery",
    "first_name": "Ada",
    "last_name": "Reader",
}


async def test_registration_returns_user_and_tokens(client: AsyncClient) -> None:
    response = await client.post("/auth/register", json=USER_DATA)

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == USER_DATA["email"]
    assert body["user"]["username"] == USER_DATA["username"]
    assert body["access_token"]
    assert body["refresh_token"]
    assert "password" not in body["user"]


async def test_login_refresh_and_protected_route(client: AsyncClient) -> None:
    await client.post("/auth/register", json=USER_DATA)
    login = await client.post(
        "/auth/login", json={"email": USER_DATA["email"], "password": USER_DATA["password"]}
    )

    assert login.status_code == 200
    tokens = login.json()
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    refreshed = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert me.status_code == 200
    assert me.json()["first_name"] == USER_DATA["first_name"]
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]


async def test_invalid_credentials_are_rejected(client: AsyncClient) -> None:
    await client.post("/auth/register", json=USER_DATA)
    response = await client.post(
        "/auth/login", json={"email": USER_DATA["email"], "password": "wrong-password"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


async def test_protected_route_requires_access_token(client: AsyncClient) -> None:
    response = await client.get("/auth/me")

    assert response.status_code == 401
