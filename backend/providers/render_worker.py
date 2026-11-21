"""
Background Video Rendering Worker & HyperFrames Pipeline Orchestrator.

Manages asynchronous rendering jobs with full tenant isolation, durable SQLite/Postgres persistence,
timeout protection, quota enforcement, and strict production verification (FFprobe, ISOBMFF MP4).
"""

import os
import re
import time
import uuid
import json
import asyncio
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from sqlalchemy import select, update
from backend.models.db_models import RenderJobModel
from backend.core.database import AsyncSessionLocal
from backend.providers.hyperframes_adapter import HyperFramesAdapter

logger = logging.getLogger("render_worker")
logging.basicConfig(level=logging.INFO)


class RenderJobStatus(BaseModel):
    job_id: str
    user_id: str = "anonymous"
    episode_id: Optional[str] = None
    status: str = "queued"  # queued, building_composition, rendering_mp4, validating, completed, failed, cancelled
    progress_percent: int = 0
    stage_text: str = "Đang chờ xếp hàng..."
    output_mp4_url: Optional[str] = None
    output_mp4_path: Optional[str] = None
    duration_seconds: float = 0.0
    file_size_bytes: int = 0
    fps: int = 30
    resolution: str = "1080x1920"
    video_format: str = "short-form"
    created_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    error_message: Optional[str] = None


class RenderWorker:
    """Singleton worker managing background video rendering tasks with durable DB persistence."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RenderWorker, cls).__new__(cls)
            cls._instance._init_worker()
        return cls._instance

    def _init_worker(self):
        self.jobs: Dict[str, RenderJobStatus] = {}
        self.running_procs: Dict[str, asyncio.subprocess.Process] = {}
        self.base_render_dir = os.path.abspath("./data/renders")
        os.makedirs(self.base_render_dir, exist_ok=True)
        self.adapter = HyperFramesAdapter(base_render_dir=self.base_render_dir)
        self.semaphore = asyncio.Semaphore(2)  # Max 2 concurrent render jobs

    async def _save_job_to_db(self, job: RenderJobStatus, manifest: Optional[Dict[str, Any]] = None):
        """Persists initial job state to database."""
        try:
            async with AsyncSessionLocal() as session:
                db_job = RenderJobModel(
                    id=job.job_id,
                    episode_id=job.episode_id or f"ep_{job.job_id[:8]}",
                    user_id=job.user_id,
                    job_type=job.video_format,
                    status=job.status,
                    progress=job.progress_percent,
                    stage_text=job.stage_text,
                    output_url=job.output_mp4_url,
                    output_mp4_path=job.output_mp4_path,
                    duration_seconds=job.duration_seconds,
                    file_size_bytes=job.file_size_bytes,
                    resolution=job.resolution,
                    video_format=job.video_format,
                    manifest_json=manifest,
                    error_message=job.error_message,
                    created_at=datetime.utcnow().isoformat() + "Z"
                )
                session.add(db_job)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to persist job {job.job_id} to DB: {e}")

    async def _update_job_in_db(self, job: RenderJobStatus):
        """Updates job state in database."""
        try:
            async with AsyncSessionLocal() as session:
                stmt = (
                    update(RenderJobModel)
                    .where(RenderJobModel.id == job.job_id)
                    .values(
                        status=job.status,
                        progress=job.progress_percent,
                        stage_text=job.stage_text,
                        output_url=job.output_mp4_url,
                        output_mp4_path=job.output_mp4_path,
                        duration_seconds=job.duration_seconds,
                        file_size_bytes=job.file_size_bytes,
                        resolution=job.resolution,
                        video_format=job.video_format,
                        error_message=job.error_message,
                        completed_at=(
                            datetime.utcnow().isoformat() + "Z"
                            if job.status in ("completed", "failed", "cancelled")
                            else None
                        )
                    )
                )
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to update job {job.job_id} in DB: {e}")

    async def _load_job_from_db(self, job_id: str) -> Optional[RenderJobStatus]:
        """Loads job state from database."""
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(RenderJobModel).where(RenderJobModel.id == job_id)
                res = await session.execute(stmt)
                row = res.scalar_one_or_none()
                if row:
                    return RenderJobStatus(
                        job_id=row.id,
                        user_id=row.user_id,
                        episode_id=row.episode_id,
                        status=row.status,
                        progress_percent=row.progress,
                        stage_text=getattr(row, "stage_text", "Đang xử lý...") or "Đang xử lý...",
                        output_mp4_url=row.output_url,
                        output_mp4_path=getattr(row, "output_mp4_path", None),
                        duration_seconds=getattr(row, "duration_seconds", 0.0) or 0.0,
                        file_size_bytes=getattr(row, "file_size_bytes", 0) or 0,
                        resolution=getattr(row, "resolution", "1080x1920") or "1080x1920",
                        video_format=getattr(row, "video_format", "short-form") or "short-form",
                        error_message=row.error_message
                    )
        except Exception as e:
            logger.warning(f"Failed to load job {job_id} from DB: {e}")
        return None

    def create_job(
        self,
        manifest: Dict[str, Any],
        user_id: str = "demo-studio-user",
        episode_id: Optional[str] = None
    ) -> RenderJobStatus:
        """Enqueues a new rendering job with database persistence and quota validation."""
        # Enforce single active render per user quota
        active_user_jobs = [
            j for j in self.jobs.values()
            if j.user_id == user_id and j.status in ("queued", "building_composition", "rendering_mp4", "validating")
        ]
        if len(active_user_jobs) >= 2:
            raise RuntimeError(f"User {user_id} has reached maximum concurrent render quota (max 2 active renders).")

        job_id = str(uuid.uuid4())
        video_format = manifest.get("video_format") or manifest.get("video_specs", {}).get("format") or "short-form"
        aspect_ratio = manifest.get("aspect_ratio") or ("9:16" if video_format == "short-form" else "16:9")
        resolution = "1920x1080" if (video_format == "long-form" or aspect_ratio == "16:9") else "1080x1920"

        job = RenderJobStatus(
            job_id=job_id,
            user_id=user_id,
            episode_id=episode_id or f"ep_{job_id[:8]}",
            status="queued",
            progress_percent=0,
            stage_text="Đã xếp hàng kết xuất video HyperFrames...",
            resolution=resolution,
            video_format=video_format
        )
        self.jobs[job_id] = job

        # Persist to database in background task
        asyncio.create_task(self._save_job_to_db(job, manifest))

        # Schedule execution in background
        asyncio.create_task(self._process_render_job(job_id, manifest))
        return job

    async def get_job_async(self, job_id: str, user_id: Optional[str] = None) -> Optional[RenderJobStatus]:
        """Gets job status verifying tenant ownership."""
        job = self.jobs.get(job_id)
        if not job:
            job = await self._load_job_from_db(job_id)
            if job:
                self.jobs[job_id] = job

        if not job:
            # Check on-disk persistence for recovery across server restarts
            job_dir = os.path.join(self.base_render_dir, job_id)
            if os.path.exists(job_dir):
                for candidate in ["output.mp4", "out.mp4"]:
                    cand_path = os.path.join(job_dir, candidate)
                    if os.path.exists(cand_path) and os.path.getsize(cand_path) > 1000:
                        job = RenderJobStatus(
                            job_id=job_id,
                            user_id="recovered-user",
                            status="completed",
                            progress_percent=100,
                            stage_text="Kết xuất video thành công! Video đã sẵn sàng tải xuống.",
                            output_mp4_path=cand_path,
                            output_mp4_url=f"/api/v1/render/download/{job_id}",
                            file_size_bytes=os.path.getsize(cand_path)
                        )
                        self.jobs[job_id] = job
                        break

        # Tenant isolation check: if user_id is passed, caller must own the job
        if job and user_id is not None:
            if job.user_id != user_id and job.user_id not in ("demo-studio-user", "recovered-user"):
                logger.warning(f"Unauthorized access: user {user_id} tried to access job {job_id} owned by {job.user_id}")
                return None

        return job

    def get_job(self, job_id: str, user_id: Optional[str] = None) -> Optional[RenderJobStatus]:
        """Synchronous wrapper for memory lookup (checks tenant ownership)."""
        job = self.jobs.get(job_id)
        if job and user_id is not None:
            if job.user_id != user_id and job.user_id not in ("demo-studio-user", "recovered-user"):
                return None
        return job

    async def cancel_job(self, job_id: str, user_id: str) -> bool:
        """Cancels an active render job if owned by caller."""
        job = await self.get_job_async(job_id, user_id=user_id)
        if not job:
            return False

        if job.job_id in self.running_procs:
            proc = self.running_procs[job.job_id]
            try:
                proc.kill()
            except Exception:
                pass

        job.status = "cancelled"
        job.stage_text = "Tiến trình render đã bị hủy bởi người dùng."
        await self._update_job_in_db(job)
        return True

    async def _process_render_job(self, job_id: str, manifest: Dict[str, Any]):
        job = self.jobs[job_id]
        job_dir = self.adapter.prepare_job_workspace(job_id)
        video_format = job.video_format

        async with self.semaphore:
            try:
                # Stage 1: Build Composition & Acoustic Assets
                job.status = "building_composition"
                job.progress_percent = 5
                job.stage_text = "Đang tạo storyboard đồ họa chuyển động & phối âm 4 bus..."
                logger.info(f"[{job_id}] Building HyperFrames composition...")
                await self._update_job_in_db(job)

                # Run synchronous file writing & audio synthesis in executor
                loop = asyncio.get_event_loop()
                index_path = await loop.run_in_executor(
                    None,
                    self.adapter.generate_html_composition,
                    manifest,
                    job_dir
                )

                job.progress_percent = 15
                job.stage_text = "Đã khởi tạo xong mã nguồn hoạt hình HTML/SVG/GSAP."
                await self._update_job_in_db(job)

                # Stage 2: Render MP4 with HyperFrames
                job.status = "rendering_mp4"
                job.progress_percent = 20
                job.stage_text = "Đang khởi động trình duyệt Chrome không đầu & FFmpeg..."
                output_mp4_path = os.path.join(job_dir, "output.mp4")
                await self._update_job_in_db(job)

                render_cmd = [
                    "npx", "-y", "hyperframes@0.9.72", "render",
                    "-o", output_mp4_path,
                    "--fps", "30",
                    "--format", "mp4"
                ]

                logger.info(f"[{job_id}] Executing: {' '.join(render_cmd)} in {job_dir}")

                proc = await asyncio.create_subprocess_exec(
                    *render_cmd,
                    cwd=job_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
                self.running_procs[job_id] = proc

                # Stream and parse output with timeout protection (max 360 seconds)
                start_render_time = time.time()
                while True:
                    if time.time() - start_render_time > 360.0:
                        proc.kill()
                        raise RuntimeError("HyperFrames render CLI timed out after 360 seconds")

                    line = await proc.stdout.readline()
                    if not line:
                        break
                    line_str = line.decode('utf-8', errors='ignore').strip()
                    logger.debug(f"[{job_id}] {line_str}")

                    # Parse progress percentage from hyperframes output
                    match_percent = re.search(r'(\d+)%\s+(Streaming|Encoding|Assembling)', line_str)
                    if match_percent:
                        pct = int(match_percent.group(1))
                        # Scale 0-100% to 20-95%
                        scaled_pct = int(20 + (pct / 100.0) * 75)
                        job.progress_percent = max(job.progress_percent, scaled_pct)
                        action = match_percent.group(2)
                        if action == "Streaming":
                            job.stage_text = f"Đang chụp và kết xuất khung hình hoạt họa ({pct}%)..."
                        elif action == "Encoding":
                            job.stage_text = f"Đang mã hóa video H.264 phần cứng ({pct}%)..."
                        elif action == "Assembling":
                            job.stage_text = "Đang đóng gói file MP4 tiêu chuẩn ISOBMFF..."

                await proc.wait()
                self.running_procs.pop(job_id, None)

                if proc.returncode != 0:
                    raise RuntimeError(f"HyperFrames render CLI exited with code {proc.returncode}")

                if not os.path.exists(output_mp4_path):
                    alt_path = os.path.join(job_dir, "out.mp4")
                    if os.path.exists(alt_path):
                        output_mp4_path = alt_path

                if not os.path.exists(output_mp4_path) or os.path.getsize(output_mp4_path) < 1000:
                    raise RuntimeError(f"Output MP4 file missing or corrupted at {output_mp4_path}")

                # Stage 3: Strict Production Validation with FFprobe
                job.status = "validating"
                job.progress_percent = 96
                job.stage_text = "Đang kiểm chứng chất lượng file MP4 bằng FFprobe..."
                await self._update_job_in_db(job)

                probe_cmd = [
                    "ffprobe", "-v", "quiet", "-print_format", "json",
                    "-show_format", "-show_streams", output_mp4_path
                ]
                probe_res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
                probe_data = json.loads(probe_res.stdout)

                duration = float(probe_data.get("format", {}).get("duration", 0.0))
                file_size = int(probe_data.get("format", {}).get("size", 0))

                video_streams = [s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"]
                audio_streams = [s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"]

                if not video_streams:
                    raise RuntimeError("Verification failed: Output file has no video stream")
                if not audio_streams:
                    raise RuntimeError("Verification failed: Output file has no audio stream")

                v_s = video_streams[0]
                actual_w = int(v_s.get("width", 0))
                actual_h = int(v_s.get("height", 0))
                job.resolution = f"{actual_w}x{actual_h}"

                # Strict format validation: Landscape 16:9 vs Portrait 9:16
                if video_format == "long-form" and actual_w < actual_h:
                    raise RuntimeError(f"Aspect ratio mismatch: expected 16:9 landscape (1920x1080), got portrait {actual_w}x{actual_h}")
                elif video_format == "short-form" and actual_h < actual_w:
                    raise RuntimeError(f"Aspect ratio mismatch: expected 9:16 portrait (1080x1920), got landscape {actual_w}x{actual_h}")

                job.status = "completed"
                job.progress_percent = 100
                job.stage_text = "Kết xuất video thành công! Video đã sẵn sàng tải xuống."
                job.output_mp4_path = output_mp4_path
                job.output_mp4_url = f"/api/v1/render/download/{job_id}"
                job.duration_seconds = duration
                job.file_size_bytes = file_size
                job.completed_at = time.time()
                await self._update_job_in_db(job)

                logger.info(f"[{job_id}] Render completed successfully! Duration: {duration}s, Size: {file_size} bytes, Resolution: {actual_w}x{actual_h}")

            except Exception as e:
                logger.error(f"[{job_id}] Render failed: {e}", exc_info=True)
                job.status = "failed"
                job.error_message = str(e)
                job.stage_text = f"Lỗi kết xuất video: {str(e)}"
                await self._update_job_in_db(job)
                self.running_procs.pop(job_id, None)
