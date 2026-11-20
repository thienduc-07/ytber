"""
Video Rendering API Router powered by HyperFrames.

Provides endpoints to enqueue render jobs, stream real-time progress,
and download broadcast-ready MP4 files.
"""

import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from backend.providers.render_worker import RenderWorker, RenderJobStatus

router = APIRouter(prefix="/api/v1/render", tags=["Render"])
worker = RenderWorker()


class RenderRequest(BaseModel):
    manifest: Dict[str, Any]


@router.post("/start", response_model=Dict[str, Any])
async def start_render_job(req: RenderRequest):
    """
    Submits a video rendering job to the HyperFrames queue.
    """
    if not req.manifest or not req.manifest.get("scenes"):
        raise HTTPException(status_code=400, detail="SceneManifest must contain at least 1 scene")

    job = worker.create_job(req.manifest)
    return {
        "job_id": job.job_id,
        "status": job.status,
        "stage_text": job.stage_text,
        "progress_percent": job.progress_percent
    }


@router.get("/status/{job_id}", response_model=Dict[str, Any])
async def get_render_status(job_id: str):
    """
    Returns real-time rendering progress and download information for a job.
    """
    job = worker.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Render job {job_id} not found")

    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress_percent": job.progress_percent,
        "stage_text": job.stage_text,
        "output_mp4_url": job.output_mp4_url,
        "duration_seconds": job.duration_seconds,
        "file_size_bytes": job.file_size_bytes,
        "error_message": job.error_message
    }


@router.api_route("/download/{job_id}", methods=["GET", "HEAD"])
async def download_rendered_mp4(job_id: str):
    """
    Streams and downloads the final rendered MP4 video.
    """
    job = worker.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Render job {job_id} not found")

    if job.status != "completed" or not job.output_mp4_path or not os.path.exists(job.output_mp4_path):
        raise HTTPException(status_code=400, detail=f"Render job {job_id} is not completed or file is missing")

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
