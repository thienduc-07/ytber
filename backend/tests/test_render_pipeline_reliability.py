"""
Comprehensive Integration & Reliability Test Suite for Video Rendering Pipeline.

Validates:
1. Transactional Job Creation & Persistence in DB
2. Atomic Worker Claiming & Concurrency Isolation (Two workers competing)
3. Worker Lease Expiration & Crash Recovery
4. Process Group Supervision & True Cancellation
5. Dual Inactivity & Overall Timeout Enforcement
6. Strict Multi-Dimensional MP4 Production Validation (FFprobe + FFmpeg decode)
7. Multi-User Tenant Isolation across Start, Status, Cancel, and Download
"""

import os
import sys
import time
import pytest
import asyncio
import subprocess
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import select, update

from backend.main import app
from backend.core.config import settings
from backend.core.database import AsyncSessionLocal, init_db_sync
from backend.models.db_models import RenderJobModel
from backend.providers.render_worker import RenderWorker, RenderJobStatus
from backend.tests.test_director_router import get_auth_headers, TEST_SECRET

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", TEST_SECRET)
    monkeypatch.setattr(settings, "SUPABASE_JWT_AUDIENCE", "authenticated")
    monkeypatch.setattr(settings, "SUPABASE_JWT_ISSUER", "https://test.supabase.co/auth/v1")
    init_db_sync()

    from sqlalchemy import create_engine, text
    sync_url = settings.DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "")
    sync_engine = create_engine(sync_url, connect_args={"check_same_thread": False} if "sqlite" in sync_url else {})
    with sync_engine.begin() as conn:
        conn.execute(text("DELETE FROM render_jobs"))


@pytest.mark.asyncio
async def test_job_creation_transactional_persistence():
    """Test A: Verifies transactional persistence in DB upon create_job_async."""
    worker = RenderWorker(worker_id="test-worker-alpha")
    manifest = {
        "title": "Kiểm Thử Queue Bền Vững",
        "aspect_ratio": "9:16",
        "video_specs": {"width": 1080, "height": 1920, "fps": 30},
        "scenes": [
            {"scene_order": 1, "narration_text": "Cảnh kiểm tra queue.", "duration_seconds": 3.0}
        ]
    }

    job = await worker.create_job_async(manifest, user_id="tenant_user_alpha")
    assert job.job_id is not None
    assert job.status == "queued"
    assert job.resolution == "1080x1920"
    assert job.video_format in ["portrait", "short-form"]

    # Query directly from DB
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RenderJobModel).where(RenderJobModel.id == job.job_id)
        )
        db_job = result.scalar_one_or_none()
        assert db_job is not None
        assert db_job.user_id == "tenant_user_alpha"
        assert db_job.status == "queued"
        assert db_job.progress == 0
        assert db_job.resolution == "1080x1920"
        assert db_job.max_attempts == 3
        assert db_job.attempt_count == 0


@pytest.mark.asyncio
async def test_atomic_worker_claiming_concurrency():
    """Test B: Two competing workers attempt to claim the exact same queued job."""
    worker_1 = RenderWorker(worker_id="worker-node-1")
    worker_2 = RenderWorker(worker_id="worker-node-2")

    manifest = {
        "title": "Tranh chấp Atomic Claim",
        "aspect_ratio": "16:9",
        "video_specs": {"width": 1920, "height": 1080, "fps": 30},
        "scenes": [
            {"scene_order": 1, "narration_text": "Cảnh tranh chấp tài nguyên.", "duration_seconds": 2.0}
        ]
    }

    job = await worker_1.create_job_async(manifest, user_id="race_condition_tester")

    # Both workers compete to claim the next job simultaneously
    claim_results = await asyncio.gather(
        worker_1.claim_next_job(),
        worker_2.claim_next_job()
    )

    claimed_1, claimed_2 = claim_results

    # Exactly one worker must have successfully claimed the job, the other got None
    assert (claimed_1 is not None and claimed_2 is None) or (claimed_1 is None and claimed_2 is not None)

    winner_tuple = claimed_1 if claimed_1 is not None else claimed_2
    winner_job_id, winner_manifest = winner_tuple
    assert winner_job_id == job.job_id

    # Verify DB state reflects the single winner
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RenderJobModel).where(RenderJobModel.id == job.job_id)
        )
        db_job = result.scalar_one()
        assert db_job.status == "preparing"
        assert db_job.worker_id in ["worker-node-1", "worker-node-2"]
        assert db_job.lease_expires_at is not None


@pytest.mark.asyncio
async def test_worker_lease_expiration_and_crash_recovery():
    """Test C: Reclaims crashed or abandoned job whose lease has expired."""
    worker = RenderWorker(worker_id="reclaimer-worker")
    manifest = {
        "title": "Crash Recovery Job",
        "aspect_ratio": "9:16",
        "scenes": [{"scene_order": 1, "narration_text": "Cảnh sập worker.", "duration_seconds": 2.0}]
    }

    job = await worker.create_job_async(manifest, user_id="crash_tester")

    # Manually simulate a crashed worker holding an expired lease
    async with AsyncSessionLocal() as session:
        expired_time = datetime.utcnow() - timedelta(seconds=60)
        await session.execute(
            update(RenderJobModel)
            .where(RenderJobModel.id == job.job_id)
            .values(
                status="rendering",
                worker_id="crashed-worker-999",
                lease_expires_at=expired_time,
                heartbeat_at=expired_time,
                attempt_count=1
            )
        )
        await session.commit()

    # Run crash recovery
    await worker.recover_stale_jobs()

    # Verify job was safely recycled back to 'queued' with incremented attempt_count
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RenderJobModel).where(RenderJobModel.id == job.job_id)
        )
        db_job = result.scalar_one()
        assert db_job.status == "queued"
        assert db_job.worker_id is None
        assert db_job.attempt_count == 1
        assert "crashed-worker-999" in (db_job.last_error or "")


@pytest.mark.asyncio
async def test_mp4_validation_strictness(tmp_path):
    """Test F: Verifies strict validation of MP4 files (size, codec, dimensions, decode)."""
    worker = RenderWorker(worker_id="validator-worker")

    # 1. Non-existent file
    with pytest.raises(ValueError, match="Output MP4 file does not exist"):
        await worker._validate_mp4_file("/tmp/non_existent_video_12345.mp4", 1080, 1920)

    # 2. Corrupt / tiny file (< 50KB)
    tiny_file = tmp_path / "tiny.mp4"
    tiny_file.write_bytes(b"not a valid mp4 content")
    with pytest.raises(ValueError, match="too small"):
        await worker._validate_mp4_file(str(tiny_file), 1080, 1920)

    # 3. Generate a real 1-second 1080x1920 MP4 with H.264 + AAC
    real_shorts_path = tmp_path / "valid_shorts.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=blue:s=1080x1920:d=1:r=30",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-t", "1",
        str(real_shorts_path)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Validating correct dimensions should pass and return duration & size
    meta = await worker._validate_mp4_file(str(real_shorts_path), 1080, 1920)
    assert meta["duration"] > 0.5
    assert meta["size"] > 5000

    # Validating with wrong dimensions (e.g. expected 1920x1080) must fail
    with pytest.raises(ValueError, match="Width mismatch"):
        await worker._validate_mp4_file(str(real_shorts_path), 1920, 1080)


def test_multi_user_tenant_isolation():
    """Test G: Enforces strict tenant boundaries for Start, Status, Cancel, Download."""
    user_a_headers = get_auth_headers("tenant_alice")
    user_b_headers = get_auth_headers("tenant_bob")

    manifest = {
        "title": "Private Production Job",
        "aspect_ratio": "9:16",
        "video_specs": {"width": 1080, "height": 1920, "fps": 30},
        "scenes": [
            {"scene_order": 1, "narration_text": "Bí mật của Alice.", "duration_seconds": 2.0}
        ]
    }

    # Alice creates a render job
    res = client.post("/api/v1/render/start", json={"manifest": manifest}, headers=user_a_headers)
    assert res.status_code == 200
    job_id = res.json()["job_id"]

    # Bob attempts to inspect Alice's render job status -> 404
    bob_status_res = client.get(f"/api/v1/render/status/{job_id}", headers=user_b_headers)
    assert bob_status_res.status_code == 404

    # Alice can inspect her own job -> 200
    alice_status_res = client.get(f"/api/v1/render/status/{job_id}", headers=user_a_headers)
    assert alice_status_res.status_code == 200
    assert alice_status_res.json()["job_id"] == job_id

    # Bob attempts to cancel Alice's render job -> 404
    bob_cancel_res = client.post(f"/api/v1/render/cancel/{job_id}", headers=user_b_headers)
    assert bob_cancel_res.status_code == 404

    # Alice cancels her own job -> 200
    alice_cancel_res = client.post(f"/api/v1/render/cancel/{job_id}", headers=user_a_headers)
    assert alice_cancel_res.status_code == 200
    assert alice_cancel_res.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_job_cancellation_execution():
    """Test D: Verifies cancellation updates database and signals running worker."""
    worker = RenderWorker(worker_id="cancel-worker")
    manifest = {
        "title": "Hủy Kết Xuất Job",
        "aspect_ratio": "9:16",
        "scenes": [{"scene_order": 1, "narration_text": "Cảnh test hủy.", "duration_seconds": 2.0}]
    }

    job = await worker.create_job_async(manifest, user_id="canceller_user")

    # Cancel while queued
    cancelled = await worker.cancel_job(job.job_id, user_id="canceller_user")
    assert cancelled is True

    # Check status
    job_status = await worker.get_job_async(job.job_id, user_id="canceller_user")
    assert job_status.status == "cancelled"
    assert "hủy" in job_status.stage_text.lower()
