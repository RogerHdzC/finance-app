def register_user(client, *, username="jdoe", email="john@doe.com", password="Str0ngPassw0rd!"):
    payload = {
        "name": "John",
        "lastname": "Doe",
        "username": username,
        "email": email,
        "password": password,
    }
    return client.post("/api/v1/auth/register", json=payload)


def login_user(client, *, identifier="jdoe", password="Str0ngPassw0rd!"):
    return client.post("/api/v1/auth/login", json={"identifier": identifier, "password": password})


def test_register_201(client):
    res = register_user(client)
    assert res.status_code == 201
    body = res.json()
    assert body["id"]
    assert body["username"] == "jdoe"
    assert body["email"] == "john@doe.com"
    assert "password_hash" not in body


def test_register_password_too_weak_returns_validation_error(client):
    res = register_user(client, username="weak1", email="weak1@x.com", password="abc")
    assert res.status_code == 422

    body = res.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == "Validation failed."
    assert body["trace_id"]
    assert "errors" in body["details"]
    assert len(body["details"]["errors"]) >= 1


def test_login_200_returns_access_and_refresh(client):
    register_user(client)
    res = login_user(client)
    assert res.status_code == 200

    body = res.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"].lower() == "bearer"
    assert body["expires_in"] > 0
    assert body["user"]["username"] == "jdoe"


def test_login_invalid_credentials_401(client):
    res = login_user(client, identifier="nope", password="WrongPass123!")
    assert res.status_code == 401
    body = res.json()
    assert body["code"] in ("UNAUTHORIZED", "unauthorized", "auth.authentication_failed")
    assert body["trace_id"]


def test_refresh_200_rotates_if_enabled(client):
    register_user(client)
    login = login_user(client).json()
    old_refresh = login["refresh_token"]

    res = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert res.status_code == 200
    body = res.json()

    assert body["access_token"]
    assert body["refresh_token"]
    assert body["expires_in"] > 0

    # si rotate=true, refresh debe cambiar
    if body["refresh_token"] != old_refresh:
        reuse = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
        assert reuse.status_code in (401, 409)
