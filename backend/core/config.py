from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "production"
    PORT: int = 8000
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

    # Asset Discovery
    PEXELS_API_KEY: str = ""

settings = Settings()
