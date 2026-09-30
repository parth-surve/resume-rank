from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


engine = create_engine(
    settings.DATABASE_URL,
    # Re-test connection health before using it from the pool.
    # Primary fix for "SSL connection closed unexpectedly" during long screenings.
    pool_pre_ping=True,
    # Recycle connections after 30 minutes to prevent stale SSL sessions.
    pool_recycle=1800,
    # 3 persistent + 7 overflow = 10 total max.
    # Right-sized for one background screening thread + API request handlers.
    pool_size=3,
    max_overflow=7,
    # How long to wait for a connection before raising TimeoutError.
    pool_timeout=30,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)



class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
