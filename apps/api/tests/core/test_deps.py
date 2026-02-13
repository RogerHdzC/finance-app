# tests/core/test_deps.py
import pytest

from app.core import deps
from fastapi import HTTPException

class FakeSession:
    def __init__(self):
        self.closed = False
        self.rolled_back = False

    def close(self):
        self.closed = True

    def rollback(self):
        self.rolled_back = True


def test_get_db_yields_session_and_closes(monkeypatch):
    fake = FakeSession()

    # parchea SessionLocal() para que regrese nuestro fake
    monkeypatch.setattr(deps, "SessionLocal", lambda: fake)

    gen = deps.get_db()
    db = next(gen)

    assert db is fake

    # al cerrar el generator, debe ejecutar finally -> close()
    gen.close()
    assert fake.closed is True
    assert fake.rolled_back is False


def test_get_db_rolls_back_on_exception_and_closes(monkeypatch):
    fake = FakeSession()
    monkeypatch.setattr(deps, "SessionLocal", lambda: fake)

    gen = deps.get_db()
    _ = next(gen)

    # Simula excepción dentro del request handler (durante el "uso" del yield)
    with pytest.raises(RuntimeError):
        gen.throw(RuntimeError("boom"))

    assert fake.rolled_back is True
    assert fake.closed is True

def test_get_current_user_invalid_token(monkeypatch):
    from app.core import deps

    # fuerza verify_access_token a tronar
    def _boom(_token: str):
        raise HTTPException(status_code=401, detail="Invalid token")

    monkeypatch.setattr(deps.AuthService, "verify_access_token", _boom)

    with pytest.raises(HTTPException) as e:
        deps.get_current_user(token="bad", db=None)  # db no se usa si truena antes
    assert e.value.status_code == 401