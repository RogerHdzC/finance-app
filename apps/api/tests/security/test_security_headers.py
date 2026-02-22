def test_security_headers_present(client):
    res = client.get("/api/v1/users")

    # Headers mínimos
    assert res.headers.get("x-content-type-options") == "nosniff"
    assert res.headers.get("referrer-policy") == "no-referrer"
    assert "permissions-policy" in res.headers
    assert res.headers.get("x-frame-options") == "DENY"
