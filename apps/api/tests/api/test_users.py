# tests/api/test_users.py

def test_create_user_success(client):
    payload = {
        "name": "John",
        "lastname": "Doe",
        "username": "jdoe",
        "email": "john@doe.com",
        "password": "password123",
    }

    res = client.post("/api/v1/users", json=payload)

    assert res.status_code == 201

    body = res.json()
    assert "id" in body
    assert body["username"] == "jdoe"
    assert body["email"] == "john@doe.com"
    assert "password" not in body


def test_create_user_username_conflict(client):
    payload = {
        "name": "John",
        "lastname": "Doe",
        "username": "jdoe",
        "email": "john@doe.com",
        "password": "password123",
    }

    client.post("/api/v1/users", json=payload)
    res = client.post("/api/v1/users", json=payload)

    assert res.status_code == 409
    body = res.json()

    assert body["code"] == "user.username_already_exists"
    assert "username" in body["detail"].lower()


def test_get_users(client):
    client.post("/api/v1/users", json={
        "name": "John",
        "lastname": "Doe",
        "username": "jdoe",
        "email": "john@doe.com",
        "password": "password123",
    })

    res = client.get("/api/v1/users")

    assert res.status_code == 200
    users = res.json()

    assert isinstance(users, list)
    assert len(users) == 1
    assert users[0]["username"] == "jdoe"
