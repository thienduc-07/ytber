from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    PORT: int = 8000
    ALLOW_DEMO_AUTH: bool = True  # Enabled by default for local/self-hosted zero-config studio operation. Set False in production with Supabase.
    CORS_ORIGINS: List[str] = [
        "https://studio.yourdomain.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ]
    
    # Database (Persistent SQLite for zero-config local/self-hosted or PostgreSQL for Cloud)
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/ytber.db"
    
    # Audio Storage Directory for synthesized TTS voices
    AUDIO_STORAGE_PATH: str = "./data/audio"
    MAX_TTS_CONCURRENCY: int = 2
    TTS_TIMEOUT_SECONDS: float = 45.0
    TTS_MAX_CHUNK_CHARS: int = 250
    TTS_CACHE_ENABLED: bool = True
    TTS_CACHE_TTL_SECONDS: int = 604800  # 7 days

    # VoiceStudio Integration (Local Open-Source TTS Engine, AGPL-3.0)
    VOICESTUDIO_URL: str = "http://127.0.0.1:3900"
    VOICESTUDIO_DEFAULT_VOICE: str = "default"
    VOICESTUDIO_TIMEOUT_SECONDS: float = 30.0
    VOICESTUDIO_ENABLED: bool = True

    # Supabase Credentials (for cloud multi-tenancy)
    SUPABASE_URL: str = "https://placeholder-project.supabase.co"
    SUPABASE_ANON_KEY: str = "placeholder-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "placeholder-service-key"
    SUPABASE_JWT_SECRET: str = "placeholder-jwt-secret-min-32-chars-long"
    SUPABASE_JWT_AUDIENCE: str = "authenticated"
    SUPABASE_JWT_ISSUER: Optional[str] = None

    # AI Providers (Free Tiers)
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Asset Discovery & Storage
    PEXELS_API_KEY: str = ""
    ASSET_STORAGE_PATH: str = "./data/assets"
    MAX_ASSET_SIZE_BYTES: int = 20 * 1024 * 1024  # 20MB
    ASSET_DOWNLOAD_TIMEOUT_SECONDS: float = 15.0
    ASSET_CACHE_ENABLED: bool = True

    # HyperFrames Render Worker & Pipeline
    RENDER_STORAGE_PATH: str = "./data/renders"
    RENDER_WORKER_MODE: str = "inline"
    RENDER_MAX_CONCURRENCY: int = 2
    RENDER_OVERALL_TIMEOUT_SECONDS: float = 480.0
    RENDER_INACTIVITY_TIMEOUT_SECONDS: float = 90.0
    RENDER_LOW_MEMORY_MODE: bool = True

settings = Settings()
