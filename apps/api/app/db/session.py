from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

if not settings.database_url:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(settings.database_url,
                       future=True,
                       pool_pre_ping=True,
                       pool_size=5,
                       max_overflow=10,
                       pool_timeout=30,)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
