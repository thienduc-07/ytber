import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.core.config import settings
from backend.models.db_models import Base

# Ensure SQLite storage directory exists
if "sqlite" in settings.DATABASE_URL:
    db_file_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    if "/" in db_file_path:
        db_dir = os.path.dirname(db_file_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

# Ensure audio storage directory exists
if settings.AUDIO_STORAGE_PATH and not os.path.exists(settings.AUDIO_STORAGE_PATH):
    os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

def init_db_sync() -> None:
    """Synchronously ensure database tables exist (works for SQLite and startup)."""
    from sqlalchemy import create_engine
    sync_url = settings.DATABASE_URL.replace("+aiosqlite", "")
    sync_engine = create_engine(
        sync_url,
        connect_args={"check_same_thread": False} if "sqlite" in sync_url else {}
    )
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

async def init_db() -> None:
    """Initialize database tables idempotently."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Ensure tables exist immediately on module import (vital for TestClient & CLI tools)
try:
    init_db_sync()
except Exception as e:
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing database sessions per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
