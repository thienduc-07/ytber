import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import get_current_user_id

client = TestClient(app)

# Helper mock dependency override for user testing
def mock_get_user_a():
    return "test-user-alice"

def mock_get_user_b():
    return "test-user-bob"

def test_healthz_and_status():
    res = client.get("/healthz")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["cost_per_render"] == "$0.00"

    res_stat = client.get("/api/v1/status")
    assert res_stat.status_code == 200
    stat_data = res_stat.json()
    assert stat_data["zero_cost_verified"] is True
    assert "photo" in stat_data["supported_modalities"]

def test_security_headers():
    res = client.get("/healthz")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert "X-RateLimit-Limit" in res.headers

def test_project_crud_and_episode_flow():
    # Override user as Alice
    app.dependency_overrides[get_current_user_id] = mock_get_user_a

    # 1. Create Project
    create_res = client.post(
        "/api/v1/projects",
        json={"title": "Hồ Gươm Lịch Sử", "description": "Shorts 60s về truyền thuyết Hồ Gươm"}
    )
    assert create_res.status_code == 201
    proj = create_res.json()
    proj_id = proj["id"]
    assert proj["title"] == "Hồ Gươm Lịch Sử"
    assert proj["user_id"] == "test-user-alice"

    # 2. List Projects
    list_res = client.get("/api/v1/projects")
    assert list_res.status_code == 200
    projs = list_res.json()
    assert any(p["id"] == proj_id for p in projs)

    # 3. Update Project
    update_res = client.put(
        f"/api/v1/projects/{proj_id}",
        json={"title": "Hồ Gươm & Rùa Vàng", "status": "ready"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Hồ Gươm & Rùa Vàng"
    assert update_res.json()["status"] == "ready"

    # 4. Create Episode
    ep_res = client.post(
        f"/api/v1/projects/{proj_id}/episodes",
        json={"title": "Tập 1: Thanh Gươm Thuận Thiên", "script_raw": "Kịch bản mẫu..."}
    )
    assert ep_res.status_code == 201
    ep = ep_res.json()
    ep_id = ep["id"]
    assert ep["project_id"] == proj_id

    # 5. Update Manifest
    sample_manifest = {
        "episode_id": ep_id,
        "title": "Tập 1: Thanh Gươm Thuận Thiên",
        "total_duration_sec": 55.0,
        "total_frames": 1650,
        "scenes": []
    }
    manifest_res = client.put(
        f"/api/v1/episodes/{ep_id}/manifest",
        json={"manifest_json": sample_manifest}
    )
    assert manifest_res.status_code == 200
    assert manifest_res.json()["manifest_json"]["total_duration_sec"] == 55.0

    # 6. Delete Project
    del_res = client.delete(f"/api/v1/projects/{proj_id}")
    assert del_res.status_code == 204

    # 7. Verify deletion
    get_res = client.get(f"/api/v1/projects/{proj_id}")
    assert get_res.status_code == 404

    # Cleanup override
    app.dependency_overrides.clear()

def test_tenant_isolation():
    # Alice creates a project
    app.dependency_overrides[get_current_user_id] = mock_get_user_a
    create_res = client.post(
        "/api/v1/projects",
        json={"title": "Dự án riêng tư của Alice"}
    )
    assert create_res.status_code == 201
    proj_id = create_res.json()["id"]

    # Now Bob attempts to access Alice's project
    app.dependency_overrides[get_current_user_id] = mock_get_user_b
    get_res = client.get(f"/api/v1/projects/{proj_id}")
    assert get_res.status_code == 403
    assert "Access denied" in get_res.json()["detail"]

    # Bob attempts to delete Alice's project
    del_res = client.delete(f"/api/v1/projects/{proj_id}")
    assert del_res.status_code == 403

    app.dependency_overrides.clear()
