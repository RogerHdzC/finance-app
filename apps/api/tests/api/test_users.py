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
    assert body["id"] is not None
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

def test_create_user_email_conflict(client):
    payload1 = {
        "name": "John",
        "lastname": "Doe",
        "username": "jdoe",
        "email": "john@doe.com",
        "password": "password123",
    }
    payload2 = {
        "name": "Jane",
        "lastname": "Doe",
        "username": "jadoe",
        "email": "john@doe.com",
        "password": "password123",
    }
    client.post("/api/v1/users", json=payload1)
    res = client.post("/api/v1/users", json=payload2)
    assert res.status_code == 409
    body = res.json()
    assert body["code"] == "user.email_already_exists"
    assert "email" in body["detail"].lower()

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
    assert users["meta"]["total"] == 1
    assert users["meta"]["total_pages"] == 1
    assert len(users["user"]) == 1
    assert users["user"][0]["username"] == "jdoe"

def test_get_user_by_id_not_found(client):
    res = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")

    assert res.status_code == 404
    body = res.json()
    assert body["code"] == "user.not_found"
    assert "the requested user does not exist." in body["detail"].lower()

def test_delete_user_success(client):
    payload = {
        "name": "John",
        "lastname": "Doe",
        "username": "jdoe",
        "email": "john@doe.com",
        "password": "password123",
    }
    res = client.post("/api/v1/users", json=payload)
    user_id = res.json()["id"]
    del_res = client.delete(f"/api/v1/users/{user_id}")
    assert del_res.status_code == 204
    get_res = client.get(f"/api/v1/users/{user_id}")
    assert get_res.status_code == 404
    
def test_delete_user_not_found(client):
    res = client.delete("/api/v1/users/00000000-0000-0000-0000-000000000001")
    assert res.status_code == 404

    body = res.json()
    assert body["code"] == "user.not_found"
    assert "does not exist" in body["detail"].lower()