import importlib
import pytest
from fastapi.testclient import TestClient

from app.core.deps import get_db


@pytest.fixture
def client_strict_origin(db_session, monkeypatch):
    monkeypatch.setenv("ENFORCE_ORIGIN", "true")
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://testclient")
    monkeypatch.setenv("ALLOWED_HOSTS", "testserver,localhost,127.0.0.1")

    import app.core.config as config
    importlib.reload(config)

    import app.core.security_http as security_http
    importlib.reload(security_http)

    import app.main as main
    importlib.reload(main)

    app = main.create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_auth_endpoints_require_origin_when_enabled(client_strict_origin):
    res = client_strict_origin.post(
        "/api/v1/auth/login",
        json={"identifier": "nope", "password": "WrongPass123!"},
    )
    assert res.status_code == 403
    assert res.json()["code"] == "ORIGIN_REQUIRED"


def test_auth_endpoints_block_disallowed_origin(client_strict_origin):
    res = client_strict_origin.post(
        "/api/v1/auth/login",
        headers={"Origin": "http://evil.com"},
        json={"identifier": "nope", "password": "WrongPass123!"},
    )
    assert res.status_code == 403
    assert res.json()["code"] == "ORIGIN_NOT_ALLOWED"