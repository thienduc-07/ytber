"""
Test Suite for HyperFrames Backend Rendering Pipeline & Adapter.
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.providers.hyperframes_adapter import HyperFramesAdapter

client = TestClient(app)


def test_hyperframes_adapter_composition_generation(tmp_path):
    """Verify HyperFramesAdapter generates valid index.html, hyperframes.json, and package.json."""
    adapter = HyperFramesAdapter(base_render_dir=str(tmp_path))
    job_dir = adapter.prepare_job_workspace("test_job_123")

    mock_manifest = {
        "title": "Chiến Dịch Lịch Sử 1954",
        "genre": "historical_doc",
        "total_duration_sec": 6.0,
        "video_specs": {"width": 1080, "height": 1920, "fps": 30},
        "scenes": [
            {
                "scene_order": 1,
                "narration_text": "Bản đồ cứ điểm Điện Biên Phủ năm 1954 tại lòng chảo Tây Bắc.",
                "duration_seconds": 3.0,
                "visual_method": "map"
            },
            {
                "scene_order": 2,
                "narration_text": "Toàn quân ta gồm hàng chục nghìn chiến sĩ anh dũng kéo pháo.",
                "duration_seconds": 3.0,
                "visual_method": "infographic"
            }
        ]
    }

    index_path = adapter.generate_html_composition(mock_manifest, job_dir)
    assert os.path.exists(index_path)

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "data-resolution=\"portrait\"" in html
    assert "data-width=\"1080\"" in html
    assert "data-height=\"1920\"" in html
    assert "gsap.timeline" in html
    assert "window.__timelines[\"main\"]" in html
    assert "assets/audio/bgm.mp3" in html
    assert "subtitles-container" in html

    assert os.path.exists(os.path.join(job_dir, "hyperframes.json"))
    assert os.path.exists(os.path.join(job_dir, "package.json"))
    assert os.path.exists(os.path.join(job_dir, "assets", "audio", "bgm.mp3"))


def test_render_api_start_and_status():
    """Verify POST /api/v1/render/start and GET /api/v1/render/status/{job_id}."""
    mock_manifest = {
        "title": "Kiểm thử API Render",
        "genre": "historical_doc",
        "total_duration_sec": 4.0,
        "scenes": [
            {
                "scene_order": 1,
                "narration_text": "Kiểm thử API kết xuất video HyperFrames chất lượng cao.",
                "duration_seconds": 4.0
            }
        ]
    }

    res = client.post("/api/v1/render/start", json={"manifest": mock_manifest})
    assert res.status_code == 200
    data = res.json()
    assert "job_id" in data
    assert data["status"] in ["queued", "building_composition", "rendering_mp4"]

    job_id = data["job_id"]
    status_res = client.get(f"/api/v1/render/status/{job_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["job_id"] == job_id
    assert status_data["progress_percent"] >= 0
