from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from backend.core.security import get_current_user_id
from backend.providers.asset_discovery import AssetDiscoveryService, MediaAsset

router = APIRouter(prefix="/api/v1/assets", tags=["Asset Discovery & Research"])
asset_service = AssetDiscoveryService()

class AssetSearchResponse(BaseModel):
    query: str
    total: int
    assets: List[MediaAsset]

@router.get("/search", response_model=AssetSearchResponse)
async def search_assets(
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm ảnh/video tư liệu"),
    query: Optional[str] = Query(None, description="Từ khóa tìm kiếm (alias)"),
    limit: int = Query(default=12, ge=1, le=30),
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
    assets = await asset_service.search(query=clean_term, limit=limit)
    return AssetSearchResponse(
        query=clean_term,
        total=len(assets),
        assets=assets
    )
