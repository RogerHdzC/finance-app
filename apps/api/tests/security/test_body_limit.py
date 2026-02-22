def test_body_size_limit_returns_413(client):
    # No necesitamos mandar body real gigante; basta Content-Length
    res = client.post(
        "/api/v1/auth/login",
        headers={"Content-Length": str(1_000_001)},
        json={"identifier": "nope", "password": "WrongPass123!"},
    )

    assert res.status_code == 413
    body = res.json()
    assert body["code"] == "PAYLOAD_TOO_LARGE"
    assert body["trace_id"]
    assert body["details"]["max_bytes"] == 1_000_000
