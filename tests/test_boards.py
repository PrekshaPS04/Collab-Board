def auth_headers(client, email="a@example.com", password="secret123"):
    client.post("/users/register", json={"email": email, "password": password})
    res = client.post("/users/login", json={"email": email, "password": password})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_board(client, headers, title="My board"):
    return client.post("/boards/", json={"title": title}, headers=headers)


def test_boards_require_login(client):
    assert client.get("/boards/").status_code in (401, 403)
    assert client.post("/boards/", json={"title": "x"}).status_code in (401, 403)


def test_create_board(client):
    headers = auth_headers(client)
    res = create_board(client, headers)
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "My board"
    assert body["content"] == ""


def test_create_board_empty_title(client):
    headers = auth_headers(client)
    assert create_board(client, headers, title="").status_code == 422


def test_list_shows_only_my_boards(client):
    alice = auth_headers(client, "alice@example.com")
    bob = auth_headers(client, "bob@example.com")
    create_board(client, alice, "Alice board")
    create_board(client, bob, "Bob board")

    res = client.get("/boards/", headers=alice)
    titles = [b["title"] for b in res.json()]
    assert titles == ["Alice board"]


def test_get_board(client):
    headers = auth_headers(client)
    board_id = create_board(client, headers).json()["id"]
    res = client.get(f"/boards/{board_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == board_id


def test_get_missing_board(client):
    headers = auth_headers(client)
    assert client.get("/boards/9999", headers=headers).status_code == 404


def test_update_content_keeps_title(client):
    headers = auth_headers(client)
    board_id = create_board(client, headers, "Original").json()["id"]
    res = client.patch(f"/boards/{board_id}", json={"content": "Hello"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["content"] == "Hello"
    assert res.json()["title"] == "Original"


def test_delete_board(client):
    headers = auth_headers(client)
    board_id = create_board(client, headers).json()["id"]
    assert client.delete(f"/boards/{board_id}", headers=headers).status_code == 204
    assert client.get(f"/boards/{board_id}", headers=headers).status_code == 404


def test_cannot_access_someone_elses_board(client):
    alice = auth_headers(client, "alice@example.com")
    bob = auth_headers(client, "bob@example.com")
    board_id = create_board(client, alice).json()["id"]

    assert client.get(f"/boards/{board_id}", headers=bob).status_code == 404
    assert client.patch(f"/boards/{board_id}", json={"content": "hacked"}, headers=bob).status_code == 404
    assert client.delete(f"/boards/{board_id}", headers=bob).status_code == 404

    # Alice's board is untouched
    res = client.get(f"/boards/{board_id}", headers=alice)
    assert res.status_code == 200
    assert res.json()["content"] == ""