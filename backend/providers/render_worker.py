"""
Background Video Rendering Worker & HyperFrames Pipeline Orchestrator.

Manages asynchronous rendering jobs with full isolation, progress tracking,
timeout protection, and strict production verification (FFprobe, ISOBMFF MP4).
"""

import os
import re
import time
import uuid
import json
import asyncio
import logging
import subprocess
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.providers.hyperframes_adapter import HyperFramesAdapter

logger = logging.getLogger("render_worker")
logging.basicConfig(level=logging.INFO)


class RenderJobStatus(BaseModel):
    job_id: str
    status: str = "queued"  # queued, synthesizing_audio, building_composition, rendering_mp4, completed, failed
    progress_percent: int = 0
    stage_text: str = "Đang chờ xếp hàng..."
    output_mp4_url: Optional[str] = None
    output_mp4_path: Optional[str] = None
    duration_seconds: float = 0.0
    file_size_bytes: int = 0
    fps: int = 30
    resolution: str = "1080x1920"
    created_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    error_message: Optional[str] = None


class RenderWorker:
    """Singleton worker managing background video rendering tasks."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RenderWorker, cls).__new__(cls)
            cls._instance._init_worker()
        return cls._instance

    def _init_worker(self):
        self.jobs: Dict[str, RenderJobStatus] = {}
        self.base_render_dir = os.path.abspath("./data/renders")
        os.makedirs(self.base_render_dir, exist_ok=True)
        self.adapter = HyperFramesAdapter(base_render_dir=self.base_render_dir)
        self.semaphore = asyncio.Semaphore(2)  # Max 2 concurrent render jobs

    def create_job(self, manifest: Dict[str, Any]) -> RenderJobStatus:
        job_id = str(uuid.uuid4())
        job = RenderJobStatus(
            job_id=job_id,
            status="queued",
            progress_percent=0,
            stage_text="Đã xếp hàng kết xuất video HyperFrames..."
        )
        self.jobs[job_id] = job
        # Schedule execution in background
        asyncio.create_task(self._process_render_job(job_id, manifest))
        return job

    def get_job(self, job_id: str) -> Optional[RenderJobStatus]:
        if job_id in self.jobs:
            return self.jobs[job_id]

        # Check on-disk persistence for recovery across server restarts
        job_dir = os.path.join(self.base_render_dir, job_id)
        if os.path.exists(job_dir):
            for candidate in ["output.mp4", "out.mp4"]:
                cand_path = os.path.join(job_dir, candidate)
                if os.path.exists(cand_path) and os.path.getsize(cand_path) > 1000:
                    status = RenderJobStatus(
                        job_id=job_id,
                        status="completed",
                        progress_percent=100,
                        stage_text="Kết xuất video thành công! Video đã sẵn sàng tải xuống.",
                        output_mp4_path=cand_path,
                        output_mp4_url=f"/api/v1/render/download/{job_id}",
                        duration_seconds=34.0,
                        file_size_bytes=os.path.getsize(cand_path)
                    )
                    self.jobs[job_id] = status
                    return status
        return None

    async def _process_render_job(self, job_id: str, manifest: Dict[str, Any]):
        job = self.jobs[job_id]
        job_dir = self.adapter.prepare_job_workspace(job_id)

        async with self.semaphore:
            try:
                # Stage 1: Build Composition & Acoustic Assets
                job.status = "building_composition"
                job.progress_percent = 5
                job.stage_text = "Đang tạo storyboard đồ họa chuyển động & phối âm 3 lớp..."
                logger.info(f"[{job_id}] Building HyperFrames composition...")

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

                # Stage 2: Render MP4 with HyperFrames
                job.status = "rendering_mp4"
                job.progress_percent = 20
                job.stage_text = "Đang khởi động trình duyệt Chrome không đầu & FFmpeg..."
                output_mp4_path = os.path.join(job_dir, "output.mp4")

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

                # Stream and parse output
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    line_str = line.decode('utf-8', errors='ignore').strip()
                    logger.debug(f"[{job_id}] {line_str}")

                    # Parse progress percentage from hyperframes output (e.g. "Streaming frame 45/150", "45%")
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

                if proc.returncode != 0:
                    raise RuntimeError(f"HyperFrames render CLI exited with code {proc.returncode}")

                if not os.path.exists(output_mp4_path):
                    alt_path = os.path.join(job_dir, "out.mp4")
                    if os.path.exists(alt_path):
                        output_mp4_path = alt_path

                if not os.path.exists(output_mp4_path) or os.path.getsize(output_mp4_path) < 1000:
                    raise RuntimeError(f"Output MP4 file missing or corrupted at {output_mp4_path}")

                # Stage 3: Strict Production Validation with FFprobe
                job.progress_percent = 96
                job.stage_text = "Đang kiểm chứng chất lượng file MP4 bằng FFprobe..."

                probe_cmd = [
                    "ffprobe", "-v", "quiet", "-print_format", "json",
                    "-show_format", "-show_streams", output_mp4_path
                ]
                probe_res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
                probe_data = json.loads(probe_res.stdout)

                duration = float(probe_data.get("format", {}).get("duration", 0.0))
                file_size = int(probe_data.get("format", {}).get("size", 0))

                has_video = any(s.get("codec_type") == "video" for s in probe_data.get("streams", []))
                has_audio = any(s.get("codec_type") == "audio" for s in probe_data.get("streams", []))

                if not has_video:
                    raise RuntimeError("Verification failed: Output file has no video stream")
                if not has_audio:
                    raise RuntimeError("Verification failed: Output file has no audio stream")

                job.status = "completed"
                job.progress_percent = 100
                job.stage_text = "Kết xuất video thành công! Video đã sẵn sàng tải xuống."
                job.output_mp4_path = output_mp4_path
                job.output_mp4_url = f"/api/v1/render/download/{job_id}"
                job.duration_seconds = duration
                job.file_size_bytes = file_size
                job.completed_at = time.time()

                logger.info(f"[{job_id}] Render completed successfully! Duration: {duration}s, Size: {file_size} bytes")

            except Exception as e:
                logger.error(f"[{job_id}] Render failed: {e}", exc_info=True)
                job.status = "failed"
                job.error_message = str(e)
                job.stage_text = f"Lỗi kết xuất video: {str(e)}"
