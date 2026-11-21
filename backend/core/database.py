import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
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

# Ensure audio and asset storage directories exist
if settings.AUDIO_STORAGE_PATH and not os.path.exists(settings.AUDIO_STORAGE_PATH):
    os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
if getattr(settings, "ASSET_STORAGE_PATH", None) and not os.path.exists(settings.ASSET_STORAGE_PATH):
    os.makedirs(settings.ASSET_STORAGE_PATH, exist_ok=True)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Enforce SQLite foreign key constraints for all connection pool checkouts
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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
    sync_url = settings.DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "")
    sync_engine = create_engine(
        sync_url,
        connect_args={"check_same_thread": False} if "sqlite" in sync_url else {}
    )
    if "sqlite" in sync_url:
        @event.listens_for(sync_engine, "connect")
        def set_sync_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    Base.metadata.create_all(sync_engine)
    if "sqlite" in sync_url:
        with sync_engine.connect() as conn:
            try:
                conn.execute(text("DROP INDEX IF EXISTS ix_audio_files_filename;"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_audio_files_filename ON audio_files (filename);"))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_audio_filename_user ON audio_files (filename, user_id);"))
                # Add columns to render_jobs if they do not exist
                new_cols = [
                    ("stage_text", "VARCHAR(255) DEFAULT 'Đang chờ xếp hàng...'"),
                    ("output_mp4_path", "VARCHAR(512)"),
                    ("duration_seconds", "FLOAT DEFAULT 0.0"),
                    ("file_size_bytes", "INTEGER DEFAULT 0"),
                    ("resolution", "VARCHAR(32) DEFAULT '1080x1920'"),
                    ("video_format", "VARCHAR(32) DEFAULT 'short-form'"),
                    ("manifest_json", "JSON")
                ]
                for col_name, col_type in new_cols:
                    try:
                        conn.execute(text(f"ALTER TABLE render_jobs ADD COLUMN {col_name} {col_type};"))
                    except Exception:
                        pass
                conn.commit()
            except Exception:
                pass
    sync_engine.dispose()

async def init_db() -> None:
    """Initialize database tables idempotently."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if "sqlite" in settings.DATABASE_URL:
            try:
                await conn.execute(text("DROP INDEX IF EXISTS ix_audio_files_filename;"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_audio_files_filename ON audio_files (filename);"))
                await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_audio_filename_user ON audio_files (filename, user_id);"))
            except Exception:
                pass

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
