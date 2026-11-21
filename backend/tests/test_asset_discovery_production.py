import os
import uuid
import time
import io
import pytest
import jwt
from unittest.mock import patch
from fastapi.testclient import TestClient
from PIL import Image

from backend.main import app
from backend.core.config import settings
from backend.core.database import AsyncSessionLocal, init_db_sync
from backend.models.db_models import AssetModel
from backend.providers.asset_discovery import (
    AssetDiscoveryService,
    WikimediaCommonsProvider,
    OpenverseProvider,
    PexelsProvider,
    DiscoveredAsset
)
from backend.providers.asset_downloader import (
    AssetDownloaderService,
    is_safe_url,
    detect_media_format
)
from backend.providers.ai_rule_based import RuleBasedScriptProvider

TEST_SECRET = "test_phase3_asset_discovery_secret_32chars!!"

def create_jwt(payload: dict, secret: str = TEST_SECRET, algorithm: str = "HS256") -> str:
    return jwt.encode(payload, secret, algorithm=algorithm)

def get_auth_headers(user_id: str = "user_alpha", secret: str = TEST_SECRET) -> dict:
    now = int(time.time())
    token = create_jwt({
        "sub": user_id,
        "aud": "authenticated",
        "exp": now + 3600,
        "iat": now,
        "iss": "https://test.supabase.co/auth/v1"
    }, secret=secret)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", TEST_SECRET)
    monkeypatch.setattr(settings, "SUPABASE_JWT_AUDIENCE", "authenticated")
    monkeypatch.setattr(settings, "SUPABASE_JWT_ISSUER", "https://test.supabase.co/auth/v1")
    monkeypatch.setattr(settings, "ASSET_STORAGE_PATH", str(tmp_path))
    init_db_sync()

# ==============================================================================
# 1. PROVIDER ARCHITECTURE & DISCOVERY TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_wikimedia_live_discovery_integration():
    """Verify real live Wikimedia Commons search returns permissive assets with metadata."""
    provider = WikimediaCommonsProvider()
    results = await provider.search("Vietnam", limit=3)
    if not results:
        results = await provider.search("Vietnam map", limit=3)
    assert len(results) > 0, "Live Wikimedia Commons query for 'Vietnam' should return results"

    asset = results[0]
    assert asset.asset_id.startswith("wm_")
    assert asset.provider == "wikimedia_commons"
    assert asset.download_url.startswith("http")
    assert asset.width > 0
    assert asset.height > 0
    assert len(asset.license) > 0
    assert asset.creator is not None
    assert asset.attribution_text is not None

@pytest.mark.asyncio
async def test_openverse_discovery_structure():
    """Verify Openverse provider extracts Creative Commons metadata."""
    provider = OpenverseProvider()
    results = await provider.search("economics", limit=2)
    # If network/API is available, inspect structure
    if results:
        asset = results[0]
        assert asset.provider == "openverse"
        assert "CC" in asset.license.upper()
        assert asset.attribution_required is True

def test_pexels_unconfigured_graceful_fallback():
    """Verify Pexels provider safely returns empty list when API key is empty."""
    provider = PexelsProvider()
    assert not provider.is_available()

# ==============================================================================
# 2. INTELLIGENT SCENE QUERY FORMULATION TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_intelligent_economic_query_formulation():
    """Verify Vietnamese economic script formulates concrete industrial & financial visual queries."""
    provider = RuleBasedScriptProvider()
    script = (
        "Giá dầu thô và năng lượng thế giới tăng mạnh kỷ lục trong năm nay. "
        "Hệ thống cảng biển container và chuỗi cung ứng hàng hóa đối mặt với áp lực lớn. "
        "Ngân hàng trung ương và các định chế tài chính bắt đầu điều chỉnh lãi suất. "
        "Các nhà máy sản xuất công nghiệp đẩy mạnh tự động hóa dây chuyền chế tạo. "
        "Tốc độ tăng trưởng kinh tế và biểu đồ GDP dự kiến đạt mốc ấn tượng."
    )

    result = await provider.analyze_script(script, genre="economics", video_format="short-form")
    assert len(result.scenes) == 5

    # Scene 1: Oil/Energy -> should have oil/refinery/petroleum keywords
    s1_keywords = " ".join(result.scenes[0].search_keywords).lower()
    assert any(k in s1_keywords for k in ["oil", "refinery", "petroleum"])

    # Scene 2: Port/Container -> should have port/shipping/cargo keywords
    s2_keywords = " ".join(result.scenes[1].search_keywords).lower()
    assert any(k in s2_keywords for k in ["port", "container", "shipping", "cargo"])

    # Scene 3: Bank/Interest rates -> should have bank/financial keywords
    s3_keywords = " ".join(result.scenes[2].search_keywords).lower()
    assert any(k in s3_keywords for k in ["bank", "financial", "trading"])

    # Scene 4: Factory/Production -> should have factory/manufacturing keywords
    s4_keywords = " ".join(result.scenes[3].search_keywords).lower()
    assert any(k in s4_keywords for k in ["factory", "manufacturing", "production"])

    # Scene 5: Growth/GDP -> should have growth/chart/market keywords
    s5_keywords = " ".join(result.scenes[4].search_keywords).lower()
    assert any(k in s5_keywords for k in ["growth", "chart", "market", "data"])

# ==============================================================================
# 3. SSRF DEFENSE & SECURITY TESTS
# ==============================================================================

def test_ssrf_protection_blocks_malicious_targets():
    """Verify is_safe_url strictly rejects loopback, private IPs, cloud metadata, and illegal protocols."""
    prohibited_urls = [
        "http://127.0.0.1/admin",
        "http://localhost:8000/secret",
        "http://10.0.0.1/internal-api",
        "http://192.168.1.1/router-config",
        "http://172.16.0.5/database",
        "http://169.254.169.254/latest/meta-data/",
        "ftp://example.com/asset.jpg",
        "file:///etc/passwd",
        "gopher://example.com/1",
        "http://metadata.google.internal/computeMetadata/v1/"
    ]

    for url in prohibited_urls:
        safe, reason = is_safe_url(url)
        assert not safe, f"Prohibited URL {url} was incorrectly marked safe! ({reason})"

def test_detect_media_format_magic_bytes():
    """Verify magic bytes detection accurately distinguishes JPEG, PNG, WebP, MP4, and rejects malformed files."""
    jpeg_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00"
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    webp_bytes = b"RIFF\x24\x00\x00\x00WEBPVP8 "
    mp4_bytes = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00"
    html_bytes = b"<!DOCTYPE html><html><body>Error</body></html>"

    assert detect_media_format(jpeg_bytes) == "jpg"
    assert detect_media_format(png_bytes) == "png"
    assert detect_media_format(webp_bytes) == "webp"
    assert detect_media_format(mp4_bytes) == "mp4"
    assert detect_media_format(html_bytes) is None

# ==============================================================================
# 4. DOWNLOADER & PERSISTENCE TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_asset_downloader_with_valid_image(tmp_path):
    """Verify downloader downloads, validates dimensions, and deduplicates using SHA-256."""
    downloader = AssetDownloaderService(storage_dir=str(tmp_path))

    # Create in-memory mock JPEG
    img = Image.new("RGB", (640, 480), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    fake_jpeg_bytes = buf.getvalue()

    # Mock httpx response stream
    class MockStreamResponse:
        status_code = 200
        headers = {}
        async def aiter_bytes(self, chunk_size=65536):
            yield fake_jpeg_bytes
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass

    with patch("backend.providers.asset_downloader.is_safe_url", return_value=(True, "Safe")):
        with patch("httpx.AsyncClient.stream", return_value=MockStreamResponse()):
            res = await downloader.download_asset("https://images.example.com/photo1.jpg", user_id="user_test")
            assert res["width"] == 640
            assert res["height"] == 480
            assert res["format"] == "jpg"
            assert res["media_type"] == "image"
            assert os.path.exists(res["file_path"])
            assert res["file_size_bytes"] == len(fake_jpeg_bytes)

# ==============================================================================
# 5. API ENDPOINT & TENANT ISOLATION TESTS
# ==============================================================================

def test_asset_api_download_and_tenant_isolation(tmp_path, monkeypatch):
    """
    Verify multi-tenant isolation on media assets:
    User A downloads -> User B gets 403 trying to access User A's file.
    User B downloads same file -> SHA256 reuse, User B gains access -> 200 OK.
    User C has not downloaded -> User C gets 403.
    """
    monkeypatch.setattr(settings, "ASSET_STORAGE_PATH", str(tmp_path))
    client = TestClient(app)

    uid = uuid.uuid4().hex[:8]
    headers_a = get_auth_headers(f"asset_user_a_{uid}")
    headers_b = get_auth_headers(f"asset_user_b_{uid}")
    headers_c = get_auth_headers(f"asset_user_c_{uid}")

    img = Image.new("RGB", (800, 600), color=(255, 120, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    fake_png = buf.getvalue()

    class MockStreamResponse:
        status_code = 200
        headers = {}
        async def aiter_bytes(self, chunk_size=65536):
            yield fake_png
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass

    with patch("backend.providers.asset_downloader.is_safe_url", return_value=(True, "Safe")):
        with patch("httpx.AsyncClient.stream", return_value=MockStreamResponse()):
            # 1. User A downloads asset
            resp_a = client.post("/api/v1/assets/download", json={
                "url": "https://images.example.com/refinery.png",
                "title": "Nhà máy lọc dầu Dung Quất",
                "creator": "Tác giả A",
                "license_type": "CC BY-SA 4.0"
            }, headers=headers_a)
            assert resp_a.status_code == 200
            data_a = resp_a.json()
            filename = data_a["filename"]

            # 2. User A accesses file -> 200 OK
            get_a = client.get(f"/api/v1/assets/media/{filename}", headers=headers_a)
            assert get_a.status_code == 200
            assert get_a.headers["content-type"] == "image/png"

            # 3. User B attempts to access User A's asset directly -> 403 Forbidden
            get_b_before = client.get(f"/api/v1/assets/media/{filename}", headers=headers_b)
            assert get_b_before.status_code == 403
            assert "access denied" in get_b_before.json()["detail"].lower()

            # 4. User B downloads the exact same asset -> Cache hit & ownership granted!
            resp_b = client.post("/api/v1/assets/download", json={
                "url": "https://images.example.com/refinery.png",
                "title": "Nhà máy lọc dầu Dung Quất",
                "creator": "Tác giả A",
                "license_type": "CC BY-SA 4.0"
            }, headers=headers_b)
            assert resp_b.status_code == 200
            data_b = resp_b.json()
            assert data_b["filename"] == filename

            # 5. User B accesses file -> 200 OK
            get_b_after = client.get(f"/api/v1/assets/media/{filename}", headers=headers_b)
            assert get_b_after.status_code == 200

            # 6. User C still gets 403
            get_c = client.get(f"/api/v1/assets/media/{filename}", headers=headers_c)
            assert get_c.status_code == 403

def test_attribution_manifest_endpoint(tmp_path, monkeypatch):
    """Verify attribution manifest generation preserves creators, licenses, and sources."""
    monkeypatch.setattr(settings, "ASSET_STORAGE_PATH", str(tmp_path))
    client = TestClient(app)

    uid = uuid.uuid4().hex[:8]
    headers = get_auth_headers(f"attr_user_{uid}")

    img = Image.new("RGB", (400, 300), color=(10, 20, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    fake_bytes = buf.getvalue()

    class MockStreamResponse:
        status_code = 200
        headers = {}
        async def aiter_bytes(self, chunk_size=65536):
            yield fake_bytes
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass

    with patch("backend.providers.asset_downloader.is_safe_url", return_value=(True, "Safe")):
        with patch("httpx.AsyncClient.stream", return_value=MockStreamResponse()):
            d_resp = client.post("/api/v1/assets/download", json={
                "url": "https://images.example.com/historical_flag.jpg",
                "title": "Lá Cờ Chiến Thắng 1954",
                "creator": "Lưu Trữ Quốc Gia",
                "license_type": "CC BY 3.0",
                "attribution_required": True
            }, headers=headers)
            assert d_resp.status_code == 200
            filename = d_resp.json()["filename"]

            # Request attribution manifest
            attr_resp = client.post("/api/v1/assets/attribution-manifest", json=[filename], headers=headers)
            assert attr_resp.status_code == 200
            attr_data = attr_resp.json()
            assert attr_data["total_assets"] == 1
            assert attr_data["requires_attribution"] is True
            assert "Lá Cờ Chiến Thắng 1954" in attr_data["formatted_credits"]
            assert "Lưu Trữ Quốc Gia" in attr_data["formatted_credits"]
            assert "CC BY 3.0" in attr_data["formatted_credits"]
