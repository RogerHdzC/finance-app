def _auth_header(client):
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
    return {"Authorization": f"Bearer {login['access_token']}"}

def test_get_users(client):
    headers = _auth_header(client)
    client.post("/api/v1/auth/register", json={
        "name": "John",
        "lastname": "Doe",
        "username": "jdoe",
        "email": "john@doe.com",
        "password": "password123",
    })

    res = client.get("/api/v1/users", headers=headers)

    assert res.status_code == 200
    users = res.json()
    assert users["meta"]["total"] == 1
    assert users["meta"]["total_pages"] == 1
    assert len(users["user"]) == 1
    assert users["user"][0]["username"] == "jdoe"

def test_get_user_by_id_not_found(client):
    headers = _auth_header(client)
    res = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000", headers=headers)

    assert res.status_code == 404
    body = res.json()
    assert body["code"] == "user.not_found"
    assert "the requested user does not exist." in body["message"].lower()

def test_delete_user_success(client):
    headers = _auth_header(client)

    payload = {
        "name": "John",
        "lastname": "Doe",
        "username": "jdoe2",
        "email": "john2@doe.com",
        "password": "Str0ngPassw0rd!",
    }
    res = client.post("/api/v1/auth/register", json=payload, headers=headers)
    user_id = res.json()["id"]
    del_res = client.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert del_res.status_code == 204
    get_res = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert get_res.status_code == 404
    
def test_delete_user_not_found(client):
    headers = _auth_header(client)
    res = client.delete("/api/v1/users/00000000-0000-0000-0000-000000000001", headers=headers)
    assert res.status_code == 404

    body = res.json()
    assert body["code"] == "user.not_found"
    assert "does not exist" in body["message"].lower()