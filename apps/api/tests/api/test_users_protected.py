def _auth_headers(client):
    client.post("/api/v1/auth/register", json={
        "name": "John",
        "lastname": "Doe",
        "username": "jdoe",
        "email": "john@doe.com",
        "password": "Str0ngPassw0rd!",
    })
    login = client.post("/api/v1/auth/login", json={
        "identifier": "jdoe",
        "password": "Str0ngPassw0rd!",
    }).json()
    return {"Authorization": f"Bearer {login['access_token']}"}, login["user"]["id"]


def test_get_users_requires_auth(client):
    res = client.get("/api/v1/users")
    assert res.status_code == 401

    body = res.json()
    assert "code" in body
    assert "message" in body
    assert "trace_id" in body


def test_get_users_200_with_auth(client):
    headers, _ = _auth_headers(client)
    res = client.get("/api/v1/users", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert "user" in body
    assert "meta" in body


def test_get_user_by_id_200(client):
    headers, user_id = _auth_headers(client)
    res = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == user_id


def test_delete_user_204(client):
    headers, user_id = _auth_headers(client)
    res = client.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert res.status_code == 204
