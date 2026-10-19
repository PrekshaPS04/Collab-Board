def register(client, email="a@example.com", password="secret123"):
    return client.post("/users/register", json={"email": email, "password": password})


def login(client, email="a@example.com", password="secret123"):
    return client.post("/users/login", json={"email": email, "password": password})


def test_register_success(client):
    res = register(client)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "a@example.com"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    register(client)
    assert register(client).status_code == 400


def test_register_short_password(client):
    assert register(client, password="123").status_code == 422


def test_login_success(client):
    register(client)
    res = login(client)
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    register(client)
    assert login(client, password="wrongpass").status_code == 401


def test_me_requires_token(client):
    res = client.get("/users/me")
    assert res.status_code in (401, 403)


def test_me_with_token(client):
    register(client)
    token = login(client).json()["access_token"]
    res = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "a@example.com"