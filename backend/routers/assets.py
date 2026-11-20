import os
import re
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Header, Query, HTTPException, status
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import get_current_user_id, decode_and_verify_supabase_jwt
from backend.models.db_models import AssetModel
from backend.providers.asset_discovery import AssetDiscoveryService, DiscoveredAsset, MediaAsset
from backend.providers.asset_downloader import AssetDownloaderService

router = APIRouter(prefix="/api/v1/assets", tags=["Asset Discovery & Research"])
asset_service = AssetDiscoveryService()
downloader_service = AssetDownloaderService()

class AssetSearchResponse(BaseModel):
    query: str
    total: int
    assets: List[DiscoveredAsset]

class DownloadAssetRequest(BaseModel):
    url: str = Field(..., description="URL bên ngoài của hình ảnh hoặc video tư liệu cần tải xuống")
    title: Optional[str] = "Tư liệu nghiên cứu"
    provider: Optional[str] = "external"
    license_type: Optional[str] = "Public Domain"
    license_url: Optional[str] = ""
    creator: Optional[str] = "Unknown"
    attribution_required: bool = True
    attribution_text: Optional[str] = ""
    media_type: str = Field(default="image", description="image hoặc video")

class DownloadAssetResponse(BaseModel):
    asset_id: str
    sha256: str
    filename: str
    local_url: str
    file_size_bytes: int
    width: int
    height: int
    media_type: str
    provider: str
    title: str
    creator: str
    license_type: str
    license_url: str
    attribution_required: bool
    attribution_text: str

class AttributionItem(BaseModel):
    title: str
    creator: str
    provider: str
    license_type: str
    license_url: Optional[str] = ""
    source_url: Optional[str] = ""
    attribution_required: bool
    attribution_text: str

class AttributionManifestResponse(BaseModel):
    total_assets: int
    requires_attribution: bool
    formatted_credits: str
    attributions: List[AttributionItem]

@router.get("/search", response_model=AssetSearchResponse)
async def search_assets(
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm ảnh/video tư liệu"),
    query: Optional[str] = Query(None, description="Từ khóa tìm kiếm (alias)"),
    limit: int = Query(default=12, ge=1, le=30),
    media_type: str = Query(default="image", description="Loại tư liệu: image hoặc video"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Searches public domain and Creative Commons permissive repositories (Wikimedia Commons & Openverse)
    returning curated assets with full license metadata and attribution text.
    Protected by user authentication and SSRF filtering.
    """
    search_term = q or query
    if not search_term or len(search_term.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng cung cấp từ khóa tìm kiếm (tối thiểu 2 ký tự)"
        )

    clean_term = search_term.strip()[:100]
    assets = await asset_service.search(query=clean_term, limit=limit, media_type=media_type)
    return AssetSearchResponse(
        query=clean_term,
        total=len(assets),
        assets=assets
    )

@router.post("/download", response_model=DownloadAssetResponse)
async def download_asset_endpoint(
    req: DownloadAssetRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Securely downloads, validates magic bytes, deduplicates by SHA-256,
    and stores an external asset on disk for canvas rendering.
    Enforces SSRF prevention and tenant authorization.
    """
    try:
        download_meta = await downloader_service.download_asset(
            url=req.url,
            user_id=user_id
        )

        filename = download_meta["filename"]
        sha256 = download_meta["sha256"]

        # Link asset ownership to the requesting tenant
        stmt = select(AssetModel).where(
            AssetModel.filename == filename,
            AssetModel.user_id == user_id
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        attr_text = req.attribution_text or (
            f"Tác phẩm: {req.title} bởi {req.creator} ({req.license_type})"
            if req.attribution_required else f"Tác phẩm: {req.title} (Miền công cộng)"
        )

        if not existing:
            asset_rec = AssetModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                sha256=sha256,
                filename=filename,
                provider=req.provider or "external",
                source_url=req.url,
                media_type=download_meta["media_type"],
                title=req.title or "Tư liệu",
                creator=req.creator or "Unknown",
                license_type=req.license_type or "Public Domain",
                license_url=req.license_url or "",
                attribution_required=req.attribution_required,
                attribution_text=attr_text,
                width=download_meta["width"],
                height=download_meta["height"],
                file_size_bytes=download_meta["file_size_bytes"]
            )
            db.add(asset_rec)
            await db.commit()
            asset_id = asset_rec.id
        else:
            asset_id = existing.id

        return DownloadAssetResponse(
            asset_id=asset_id,
            sha256=sha256,
            filename=filename,
            local_url=download_meta["local_url"],
            file_size_bytes=download_meta["file_size_bytes"],
            width=download_meta["width"],
            height=download_meta["height"],
            media_type=download_meta["media_type"],
            provider=req.provider or "external",
            title=req.title or "Tư liệu",
            creator=req.creator or "Unknown",
            license_type=req.license_type or "Public Domain",
            license_url=req.license_url or "",
            attribution_required=req.attribution_required,
            attribution_text=attr_text
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi tải tài nguyên hình ảnh: {str(e)}"
        )

@router.get("/media/{filename}")
async def get_media_asset_file(
    filename: str,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Serves downloaded local media files for canvas rendering and preview.
    Protected by token authentication, tenant isolation, and path traversal checks.
    """
    # 1. Path traversal prevention
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: Path traversal characters are not permitted"
        )
    if not re.match(r"^[a-zA-Z0-9_-]+\.(jpg|jpeg|png|webp|gif|mp4|webm)$", filename.lower()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: Media format not permitted"
        )

    # 2. Extract and verify authentication token
    auth_token = None
    if authorization:
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            auth_token = parts[1]
    elif token:
        auth_token = token

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: Missing Bearer token or 'token' query parameter",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_and_verify_supabase_jwt(auth_token)
    current_user_id = str(payload.get("sub"))

    # 3. Tenant ownership verification in database
    stmt = select(AssetModel).where(
        AssetModel.filename == filename,
        AssetModel.user_id == current_user_id
    )
    res = await db.execute(stmt)
    asset_rec = res.scalar_one_or_none()

    if not asset_rec:
        # Check if the asset exists under another tenant
        stmt_any = select(AssetModel).where(AssetModel.filename == filename)
        any_rec = (await db.execute(stmt_any)).first()
        if any_rec:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this media asset"
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tập tin tư liệu không tồn tại hoặc đã hết hạn lưu trữ"
        )

    # 4. Verify physical file existence securely within storage directory
    abs_storage = os.path.abspath(getattr(settings, "ASSET_STORAGE_PATH", "./data/assets"))
    filepath = os.path.abspath(os.path.join(abs_storage, filename))

    if not filepath.startswith(abs_storage) or not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tập tin tư liệu vật lý không tồn tại"
        )

    ext = filename.split(".")[-1].lower()
    media_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
        "mp4": "video/mp4",
        "webm": "video/webm"
    }
    content_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        filepath,
        media_type=content_type,
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=86400",
        }
    )

@router.post("/attribution-manifest", response_model=AttributionManifestResponse)
async def generate_attribution_manifest(
    asset_filenames: List[str],
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates an attribution manifest and YouTube credits text for a list of asset filenames.
    Preserves original creators, permissive licenses, and source references.
    """
    if not asset_filenames:
        return AttributionManifestResponse(
            total_assets=0,
            requires_attribution=False,
            formatted_credits="Tất cả tư liệu sử dụng thuộc miền công cộng hoặc đồ họa tự sinh.",
            attributions=[]
        )

    stmt = select(AssetModel).where(
        AssetModel.filename.in_(asset_filenames),
        AssetModel.user_id == user_id
    )
    records = (await db.execute(stmt)).scalars().all()

    attributions: List[AttributionItem] = []
    lines: List[str] = [
        "=== BẢN QUYỀN VÀ NGUỒN TƯ LIỆU HÌNH ẢNH / VIDEO ===",
        "Video này sử dụng các tư liệu hình ảnh và âm thanh tuân thủ giấy phép Creative Commons và Miền công cộng:\n"
    ]

    has_required = False
    for rec in records:
        is_req = rec.attribution_required
        if is_req:
            has_required = True

        attributions.append(AttributionItem(
            title=rec.title,
            creator=rec.creator,
            provider=rec.provider,
            license_type=rec.license_type,
            license_url=rec.license_url,
            source_url=rec.source_url,
            attribution_required=is_req,
            attribution_text=rec.attribution_text
        ))

        line = f"• {rec.title} - Tác giả: {rec.creator} ({rec.license_type})"
        if rec.source_url:
            line += f" | Nguồn: {rec.source_url}"
        lines.append(line)

    lines.append("\nSản xuất tự động bởi YTBER Studio.")
    formatted_text = "\n".join(lines)

    return AttributionManifestResponse(
        total_assets=len(attributions),
        requires_attribution=has_required,
        formatted_credits=formatted_text,
        attributions=attributions
    )
