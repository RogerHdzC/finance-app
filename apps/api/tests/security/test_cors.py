def test_cors_preflight_allows_configured_origin(client):
    res = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://testclient",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )

    # Starlette suele responder 200 o 204
    assert res.status_code in (200, 204)

    # Headers CORS esperados
    assert res.headers.get("access-control-allow-origin") == "http://testclient"
    allow_methods = res.headers.get("access-control-allow-methods", "")
    assert "POST" in allow_methods


def test_cors_simple_request_sets_allow_origin(client):
    res = client.post(
        "/api/v1/auth/login",
        headers={"Origin": "http://testclient"},
        json={"identifier": "nope", "password": "WrongPass123!"},
    )

    # Tu endpoint devuelve 401 por credenciales inválidas, pero CORS debe estar
    assert res.status_code == 401
    assert res.headers.get("access-control-allow-origin") == "http://testclient"
