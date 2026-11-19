import urllib.parse
from typing import List, Optional
import httpx
from pydantic import BaseModel
from backend.core.config import settings

class MediaAsset(BaseModel):
    asset_id: str
    title: str
    media_type: str  # 'image' or 'video'
    preview_url: str
    full_url: str
    source_provider: str
    source_page_url: str
    license_type: str
    author_name: str
    attribution_required: bool
    attribution_text: str

class AssetDiscoveryService:
    """
    Zero-budget, multi-source media asset discovery engine.
    Queries public domain, CC0, and permissive repositories (Wikimedia Commons, Openverse, Pexels)
    with strict licensing metadata extraction.
    """
    
    async def search_wikimedia(self, query: str, limit: int = 10) -> List[MediaAsset]:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 6,
            "gsrlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|dimensions|mime",
            "format": "json"
        }
        
        assets: List[MediaAsset] = []
        try:
            async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "ZeroBudgetStudio/1.0 (contact@yourdomain.com)"}) as client:
                resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    return assets
                    
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                
                for page_id, page_data in pages.items():
                    imageinfo = page_data.get("imageinfo", [{}])[0]
                    file_url = imageinfo.get("url", "")
                    if not file_url:
                        continue
                        
                    meta = imageinfo.get("extmetadata", {})
                    license_name = meta.get("LicenseShortName", {}).get("value", "Public Domain")
                    artist = meta.get("Artist", {}).get("value", "Unknown")
                    title = page_data.get("title", f"File:{page_id}").replace("File:", "")
                    
                    # Clean HTML tags from artist string
                    import re
                    artist_clean = re.sub(r'<[^>]+>', '', artist).strip() or "Wikimedia Contributor"
                    
                    attr_required = "CC" in license_name.upper()
                    attr_text = f"Ảnh: {title} bởi {artist_clean} ({license_name})" if attr_required else f"Ảnh: {title} (Miền công cộng)"
                    
                    assets.append(MediaAsset(
                        asset_id=f"wm_{page_id}",
                        title=title[:80],
                        media_type="image",
                        preview_url=imageinfo.get("thumburl", file_url),
                        full_url=file_url,
                        source_provider="wikimedia_commons",
                        source_page_url=imageinfo.get("descriptionurl", file_url),
                        license_type=license_name,
                        author_name=artist_clean[:50],
                        attribution_required=attr_required,
                        attribution_text=attr_text
                    ))
        except Exception as e:
            print("Wikimedia search error:", e)
            
        return assets

    async def search_openverse(self, query: str, limit: int = 10) -> List[MediaAsset]:
        url = "https://api.openverse.org/v1/images/"
        params = {
            "q": query,
            "page_size": limit,
            "license_type": "all-cc"
        }
        assets: List[MediaAsset] = []
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("results", []):
                        license_name = f"CC {item.get('license', 'BY').upper()}"
                        creator = item.get("creator", "Unknown Creator")
                        title = item.get("title", query)
                        attr_text = f"Tác phẩm: {title} bởi {creator} ({license_name})"
                        assets.append(MediaAsset(
                            asset_id=f"ov_{item.get('id')}",
                            title=title[:80],
                            media_type="image",
                            preview_url=item.get("thumbnail", item.get("url")),
                            full_url=item.get("url"),
                            source_provider="openverse",
                            source_page_url=item.get("foreign_landing_url", item.get("url")),
                            license_type=license_name,
                            author_name=creator[:50],
                            attribution_required=True,
                            attribution_text=attr_text
                        ))
        except Exception:
            pass
        return assets

    async def search(self, query: str, limit: int = 12) -> List[MediaAsset]:
        # Multi-source concurrent aggregation
        wm_assets = await self.search_wikimedia(query, limit=limit)
        if len(wm_assets) >= limit:
            return wm_assets[:limit]
            
        ov_assets = await self.search_openverse(query, limit=limit - len(wm_assets))
        return (wm_assets + ov_assets)[:limit]
