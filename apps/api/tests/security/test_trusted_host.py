def test_trusted_host_allows_known_host(client):
    # TestClient usa Host=testserver por defecto
    res = client.get("/api/v1/users")
    assert res.status_code in (200, 401, 403, 404)  # depende de tu auth/routers, lo importante es NO 400


def test_trusted_host_blocks_unknown_host(client):
    res = client.get("/api/v1/users", headers={"Host": "evil.com"})
    # Starlette TrustedHostMiddleware responde 400
    assert res.status_code == 400
