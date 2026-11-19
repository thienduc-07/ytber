import time
from typing import Dict, Any
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.config import settings
from backend.routers.script import router as script_router
from backend.routers.assets import router as assets_router
from backend.routers.tts import router as tts_router
from backend.routers.projects import router as projects_router, episode_manifest_router

# In-memory Rate Limiting (Token Bucket / Sliding Window per IP)
# Free-tier rate limits: 60 requests per minute per client IP
_RATE_LIMIT_BUCKET: Dict[str, list] = {}
RATE_LIMIT_MAX_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60

class SecurityHeadersAndRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Rate Limiting Check
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean expired timestamps
        history = _RATE_LIMIT_BUCKET.get(client_ip, [])
        history = [ts for ts in history if now - ts < RATE_LIMIT_WINDOW_SECONDS]
        
        if len(history) >= RATE_LIMIT_MAX_REQUESTS and not request.url.path.startswith("/healthz"):
            return Response(
                content='{"detail": "Tần suất yêu cầu vượt quá giới hạn (Rate limit exceeded). Vui lòng thử lại sau giây lát."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "Retry-After": str(RATE_LIMIT_WINDOW_SECONDS),
                    "X-RateLimit-Limit": str(RATE_LIMIT_MAX_REQUESTS),
                    "X-RateLimit-Remaining": "0",
                }
            )
            
        history.append(now)
        _RATE_LIMIT_BUCKET[client_ip] = history
        remaining = max(0, RATE_LIMIT_MAX_REQUESTS - len(history))

        # 2. Process Request
        response = await call_next(request)

        # 3. Attach Security & Rate Limit Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response

app = FastAPI(
    title="Zero-Budget AI Video Studio API",
    description="Public multi-tenant API gateway for Vietnamese Shorts generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attach Security and Rate Limiting Middleware
app.add_middleware(SecurityHeadersAndRateLimitMiddleware)

# Attach CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://*.pages.dev",
        "https://zero-budget-video-studio.pages.dev"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

# Register Sub-Routers
app.include_router(script_router)
app.include_router(assets_router)
app.include_router(tts_router)
app.include_router(projects_router)
app.include_router(episode_manifest_router)

@app.get("/healthz", tags=["Health & Diagnostics"])
async def health_check():
    """Liveness probe for Cloud / Docker / Serverless orchestrators."""
    return {
        "status": "healthy",
        "service": "zero-budget-ai-video-studio-api",
        "timestamp": time.time(),
        "architecture": "Architecture C (Hybrid WebCodecs)",
        "rendering_location": "in-browser-client-side",
        "cost_per_render": "$0.00"
    }

@app.get("/api/v1/status", tags=["Health & Diagnostics"])
async def system_status():
    """Detailed capability diagnostic status."""
    return {
        "system": "Zero-Budget AI Video Studio",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "supported_modalities": [
            "photo", "stock", "archival", "map", "svg",
            "infographic", "procedural", "parallax", "toon"
        ],
        "video_specs": {
            "resolution": "1080x1920",
            "aspect_ratio": "9:16",
            "fps": 30,
            "target_duration_seconds": "55-70",
            "codec": "H.264 Main Profile Level 4.2"
        },
        "tts_voices": [
            {"id": "vi-VN-HoaiMyNeural", "gender": "Female", "region": "Northern"},
            {"id": "vi-VN-NamMinhNeural", "gender": "Male", "region": "Northern"}
        ],
        "zero_cost_verified": True
    }
