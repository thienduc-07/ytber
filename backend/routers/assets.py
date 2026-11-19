from fastapi import APIRouter, Depends, Query
from typing import List
from backend.core.security import get_current_user_id
from backend.providers.asset_discovery import AssetDiscoveryService, MediaAsset

router = APIRouter(prefix="/api/v1/assets", tags=["Asset Discovery"])
asset_service = AssetDiscoveryService()

@router.get("/search", response_model=List[MediaAsset])
async def search_assets(
    q: str = Query(..., min_length=2, max_length=100, description="Từ khóa tìm kiếm ảnh/video tư liệu"),
    limit: int = Query(default=12, ge=1, le=30),
    user_id: str = Depends(get_current_user_id)
):
    """
    Searches public domain and Creative Commons repositories (Wikimedia Commons & Openverse)
    returning curated assets with full license metadata and attribution text.
    """
    return await asset_service.search(query=q, limit=limit)
