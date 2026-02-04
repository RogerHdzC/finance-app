# tests/core/test_deps.py
import pytest

from app.core import deps


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
