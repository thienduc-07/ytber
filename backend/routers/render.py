"""
Video Rendering API Router powered by HyperFrames.

Provides endpoints to enqueue render jobs, stream real-time progress,
cancel jobs, and download broadcast-ready MP4 files with strict multi-user tenant isolation.
"""

import os
from fastapi import APIRouter, HTTPException, Depends, Header, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from backend.core.security import get_current_user_id, decode_and_verify_supabase_jwt
from backend.core.config import settings
from backend.providers.render_worker import RenderWorker

router = APIRouter(prefix="/api/v1/render", tags=["Render"])
worker = RenderWorker()


class RenderRequest(BaseModel):
    manifest: Dict[str, Any]


async def resolve_download_user_id(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
) -> str:
    """Authenticates download requests via Bearer Header or query string token."""
    raw_token = None
    if authorization and authorization.lower().startswith("bearer "):
        raw_token = authorization.split(" ")[1]
    elif token:
        raw_token = token

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required to download render output",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if (raw_token.startswith("demo-") or raw_token.startswith("guest-")):
        if getattr(settings, "ALLOW_DEMO_AUTH", False) and settings.ENVIRONMENT != "production":
            return "demo-studio-user"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Demo authentication tokens are strictly disabled in production mode.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = decode_and_verify_supabase_jwt(raw_token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing 'sub' subject claim in token")
        return str(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/start", response_model=Dict[str, Any])
async def start_render_job(
    req: RenderRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Submits a video rendering job to the HyperFrames queue with tenant isolation.
    """
    if not req.manifest or not req.manifest.get("scenes"):
        raise HTTPException(status_code=400, detail="SceneManifest must contain at least 1 scene")

    try:
        job = worker.create_job(req.manifest, user_id=user_id)
        return {
            "job_id": job.job_id,
            "status": job.status,
            "stage_text": job.stage_text,
            "progress_percent": job.progress_percent,
            "resolution": job.resolution,
            "video_format": job.video_format
        }
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))


@router.get("/status/{job_id}", response_model=Dict[str, Any])
async def get_render_status(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Returns real-time rendering progress and download information for a job.
    Enforces tenant isolation: users can only view their own jobs.
    """
    job = await worker.get_job_async(job_id, user_id=user_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Render job {job_id} not found or unauthorized access"
        )

    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress_percent": job.progress_percent,
        "stage_text": job.stage_text,
        "output_mp4_url": job.output_mp4_url,
        "duration_seconds": job.duration_seconds,
        "file_size_bytes": job.file_size_bytes,
        "resolution": job.resolution,
        "video_format": job.video_format,
        "error_message": job.error_message
    }


@router.post("/cancel/{job_id}", response_model=Dict[str, Any])
async def cancel_render_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Cancels an active render job if owned by the caller.
    """
    success = await worker.cancel_job(job_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Render job {job_id} not found or unauthorized to cancel"
        )
    return {"job_id": job_id, "status": "cancelled", "detail": "Render job cancelled successfully"}


@router.api_route("/download/{job_id}", methods=["GET", "HEAD"])
async def download_rendered_mp4(
    job_id: str,
    user_id: str = Depends(resolve_download_user_id)
):
    """
    Streams and downloads the final rendered MP4 video.
    Enforces tenant isolation: users can only download videos from their own jobs.
    """
    job = await worker.get_job_async(job_id, user_id=user_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Render job {job_id} not found or unauthorized access"
        )

    if job.status != "completed" or not job.output_mp4_path or not os.path.exists(job.output_mp4_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Render job {job_id} is not completed or output file is missing"
        )

    filename = f"video_{job_id[:8]}.mp4"
    return FileResponse(
        path=job.output_mp4_path,
        media_type="video/mp4",
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Accept-Ranges": "bytes"
        }
    )
