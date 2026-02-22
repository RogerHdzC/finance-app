# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base_class import Base

import os
import importlib

# --- Test database (SQLite in-memory) ---
SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

@pytest.fixture(scope="session", autouse=True)
def _force_test_env():
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

    os.environ["JWT_SECRET_KEY"] = "test-secret"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["JWT_EXPIRATION_DELTA_SECONDS"] = "3600"
    os.environ["JWT_ISSUER"] = "finance_api"
    os.environ["JWT_AUDIENCE"] = "finance_api_users"
    os.environ["JWT_REFRESH_EXPIRATION_SECONDS"] = "1209600"
    os.environ["JWT_REFRESH_ROTATE"] = "true"

    # Hardening defaults (CSV)
    os.environ["ALLOWED_HOSTS"] = "testserver,localhost,127.0.0.1"
    os.environ["ALLOWED_ORIGINS"] = "http://testclient"
    os.environ["MAX_BODY_BYTES"] = "1000000"
    os.environ["ENFORCE_ORIGIN"] = "false"
    yield

@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    import app.db.base
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def app():
    import app.core.config as config  # noqa: E402
    importlib.reload(config)
    import app.main as main  # noqa: E402
    importlib.reload(main)
    return main.create_app()

@pytest.fixture
def db_session():
    """
    Provides a SQLAlchemy session with rollback after each test.
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    # Start a SAVEPOINT
    session.begin_nested()

    # Restart SAVEPOINT after each commit/rollback inside the test
    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(autouse=True)
def _clean_db(db_session):
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.flush()

@pytest.fixture
def client(app, db_session):
    """
    FastAPI TestClient with overridden DB dependency.
    """
    from app.core.deps import get_db  # noqa: E402

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
