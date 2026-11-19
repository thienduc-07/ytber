from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "https://studio.yourdomain.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # Supabase Credentials
    SUPABASE_URL: str = "https://placeholder-project.supabase.co"
    SUPABASE_ANON_KEY: str = "placeholder-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "placeholder-service-key"
    SUPABASE_JWT_SECRET: str = "placeholder-jwt-secret-min-32-chars-long"

    # AI Providers (Free Tiers)
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Asset Discovery
    PEXELS_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
