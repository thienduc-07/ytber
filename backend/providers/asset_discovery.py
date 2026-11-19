import re
import urllib.parse
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel, Field

from backend.core.config import settings

class DiscoveredAsset(BaseModel):
    asset_id: str
    provider: str
    source_url: str
    download_url: str
    title: str
    description: Optional[str] = ""
    creator: str = "Unknown"
    license: str = "Public Domain"
    license_url: Optional[str] = ""
    width: int = 1920
    height: int = 1080
    media_type: str = Field(default="image", description="image or video")
    attribution_required: bool = True
    attribution_text: Optional[str] = None
    local_url: Optional[str] = None
    preview_url: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.preview_url:
            self.preview_url = self.download_url
        if not self.attribution_text:
            if self.attribution_required:
                self.attribution_text = f"Tác phẩm: {self.title} bởi {self.creator} ({self.license})"
            else:
                self.attribution_text = f"Tác phẩm: {self.title} (Miền công cộng)"

    # Backward compatibility properties with existing MediaAsset interface
    @property
    def full_url(self) -> str:
        return self.download_url

    @property
    def source_provider(self) -> str:
        return self.provider

    @property
    def source_page_url(self) -> str:
        return self.source_url

    @property
    def license_type(self) -> str:
        return self.license

    @property
    def author_name(self) -> str:
        return self.creator

# Backward compatibility alias
MediaAsset = DiscoveredAsset

class BaseAssetProvider(ABC):
    provider_name: str = "base"

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        media_type: str = "image"
    ) -> List[DiscoveredAsset]:
        """Search permissive media assets matching query."""
        pass

class WikimediaCommonsProvider(BaseAssetProvider):
    provider_name = "wikimedia_commons"

    async def search(
        self,
        query: str,
        limit: int = 10,
        media_type: str = "image"
    ) -> List[DiscoveredAsset]:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 6,  # File: namespace
            "gsrlimit": min(limit * 2, 30),
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|dimensions|mime",
            "format": "json"
        }

        assets: List[DiscoveredAsset] = []
        headers = {"User-Agent": "YTBerStudio/2.0 (media-discovery@ytber.local)"}

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    return assets

                data = resp.json()
                pages = data.get("query", {}).get("pages", {})

                for page_id, page_data in pages.items():
                    imageinfo_list = page_data.get("imageinfo", [])
                    if not imageinfo_list:
                        continue
                    imageinfo = imageinfo_list[0]
                    file_url = imageinfo.get("url", "")
                    if not file_url:
                        continue

                    mime = imageinfo.get("mime", "").lower()
                    width = int(imageinfo.get("width", 1920) or 1920)
                    height = int(imageinfo.get("height", 1080) or 1080)

                    # Filter out vector SVGs, audio, or PDFs that cannot be rendered directly in canvas
                    if mime.startswith("audio/") or mime.startswith("application/pdf") or "svg" in mime:
                        continue

                    # Media type detection
                    is_video = "video" in mime or file_url.lower().endswith((".mp4", ".webm", ".ogv"))
                    detected_type = "video" if is_video else "image"
                    if media_type == "video" and not is_video:
                        continue
                    if media_type == "image" and is_video:
                        continue

                    meta = imageinfo.get("extmetadata", {})
                    license_name = meta.get("LicenseShortName", {}).get("value", "Public Domain")
                    artist_raw = meta.get("Artist", {}).get("value", "Wikimedia Contributor")
                    desc_raw = meta.get("ImageDescription", {}).get("value", "")
                    license_url = meta.get("LicenseUrl", {}).get("value", "")

                    artist_clean = re.sub(r'<[^>]+>', '', artist_raw).strip() or "Wikimedia Contributor"
                    desc_clean = re.sub(r'<[^>]+>', '', desc_raw).strip()[:200]
                    title = page_data.get("title", f"File:{page_id}").replace("File:", "").strip()

                    # Determine attribution requirement
                    lic_lower = license_name.lower()
                    attr_required = not ("public domain" in lic_lower or "cc0" in lic_lower or "pdm" in lic_lower)

                    if attr_required:
                        attr_text = f"Tác phẩm: {title[:60]} bởi {artist_clean[:40]} ({license_name})"
                    else:
                        attr_text = f"Tác phẩm: {title[:60]} (Miền công cộng)"

                    assets.append(DiscoveredAsset(
                        asset_id=f"wm_{page_id}",
                        provider="wikimedia_commons",
                        source_url=imageinfo.get("descriptionurl", file_url),
                        download_url=file_url,
                        title=title[:100],
                        description=desc_clean,
                        creator=artist_clean[:60],
                        license=license_name,
                        license_url=license_url,
                        width=width,
                        height=height,
                        media_type=detected_type,
                        attribution_required=attr_required,
                        attribution_text=attr_text,
                        preview_url=imageinfo.get("thumburl", file_url)
                    ))

                    if len(assets) >= limit:
                        break

        except Exception as e:
            # Graceful logging without crashing aggregator
            print(f"WikimediaCommonsProvider search error: {e}")

        return assets

class OpenverseProvider(BaseAssetProvider):
    provider_name = "openverse"

    async def search(
        self,
        query: str,
        limit: int = 10,
        media_type: str = "image"
    ) -> List[DiscoveredAsset]:
        # Openverse API focuses primarily on images
        if media_type == "video":
            return []

        url = "https://api.openverse.org/v1/images/"
        params = {
            "q": query,
            "page_size": min(limit * 2, 20),
            "license_type": "all-cc"
        }
        assets: List[DiscoveredAsset] = []
        headers = {"User-Agent": "YTBerStudio/2.0 (media-discovery@ytber.local)"}

        try:
            async with httpx.AsyncClient(timeout=3.0, headers=headers) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("results", []):
                        lic = item.get("license", "by").upper()
                        license_name = f"CC {lic}"
                        creator = (item.get("creator") or "Openverse Contributor").strip()
                        title = (item.get("title") or query).strip()
                        raw_url = item.get("url", "")
                        if not raw_url:
                            continue

                        width = int(item.get("width") or 1920)
                        height = int(item.get("height") or 1080)
                        thumb = item.get("thumbnail") or raw_url
                        landing = item.get("foreign_landing_url") or raw_url
                        license_url = item.get("license_url", "")

                        attr_required = lic not in ("CC0", "PDM", "PUBLIC DOMAIN")
                        attr_text = f"Tác phẩm: {title[:60]} bởi {creator[:40]} ({license_name})"

                        assets.append(DiscoveredAsset(
                            asset_id=f"ov_{item.get('id')}",
                            provider="openverse",
                            source_url=landing,
                            download_url=raw_url,
                            title=title[:100],
                            description=f"Creative Commons visual asset from Openverse ({query})",
                            creator=creator[:60],
                            license=license_name,
                            license_url=license_url,
                            width=width,
                            height=height,
                            media_type="image",
                            attribution_required=attr_required,
                            attribution_text=attr_text,
                            preview_url=thumb
                        ))

                        if len(assets) >= limit:
                            break
        except Exception as e:
            print(f"OpenverseProvider search error: {e}")

        return assets

class PexelsProvider(BaseAssetProvider):
    provider_name = "pexels"

    def is_available(self) -> bool:
        return bool(getattr(settings, "PEXELS_API_KEY", None) and settings.PEXELS_API_KEY.strip())

    async def search(
        self,
        query: str,
        limit: int = 10,
        media_type: str = "image"
    ) -> List[DiscoveredAsset]:
        if not self.is_available():
            return []

        api_key = settings.PEXELS_API_KEY.strip()
        headers = {"Authorization": api_key, "User-Agent": "YTBerStudio/2.0"}
        assets: List[DiscoveredAsset] = []

        try:
            async with httpx.AsyncClient(timeout=3.0, headers=headers) as client:
                if media_type == "video":
                    url = "https://api.pexels.com/videos/search"
                    resp = await client.get(url, params={"query": query, "per_page": limit})
                    if resp.status_code == 200:
                        data = resp.json()
                        for v in data.get("videos", []):
                            video_files = v.get("video_files", [])
                            # Find highest quality mp4
                            hd_file = next((f for f in video_files if f.get("quality") == "hd" and f.get("file_type") == "video/mp4"), None)
                            if not hd_file and video_files:
                                hd_file = video_files[0]
                            if hd_file:
                                assets.append(DiscoveredAsset(
                                    asset_id=f"pex_v_{v.get('id')}",
                                    provider="pexels",
                                    source_url=v.get("url", ""),
                                    download_url=hd_file.get("link", ""),
                                    title=f"Pexels Video {v.get('id')}",
                                    creator=v.get("user", {}).get("name", "Pexels Creator"),
                                    license="Pexels License (Free Commercial Use)",
                                    license_url="https://www.pexels.com/license/",
                                    width=v.get("width", 1920),
                                    height=v.get("height", 1080),
                                    media_type="video",
                                    attribution_required=False,
                                    attribution_text=f"Video bởi {v.get('user', {}).get('name', 'Pexels Creator')} trên Pexels",
                                    preview_url=v.get("image", "")
                                ))
                else:
                    url = "https://api.pexels.com/v1/search"
                    resp = await client.get(url, params={"query": query, "per_page": limit})
                    if resp.status_code == 200:
                        data = resp.json()
                        for p in data.get("photos", []):
                            src = p.get("src", {})
                            assets.append(DiscoveredAsset(
                                asset_id=f"pex_p_{p.get('id')}",
                                provider="pexels",
                                source_url=p.get("url", ""),
                                download_url=src.get("original") or src.get("large2x") or src.get("large"),
                                title=p.get("alt", query) or f"Pexels Photo {p.get('id')}",
                                creator=p.get("photographer", "Pexels Creator"),
                                license="Pexels License (Free Commercial Use)",
                                license_url="https://www.pexels.com/license/",
                                width=p.get("width", 1920),
                                height=p.get("height", 1080),
                                media_type="image",
                                attribution_required=False,
                                attribution_text=f"Ảnh bởi {p.get('photographer', 'Pexels Creator')} trên Pexels",
                                preview_url=src.get("medium") or src.get("tiny")
                            ))
        except Exception as e:
            print(f"PexelsProvider search error: {e}")

        return assets

class AssetDiscoveryService:
    """
    Zero-budget, multi-source permissive media asset discovery engine.
    Aggregates Wikimedia Commons, Openverse, and optional Pexels.
    Includes resolution prioritization, deduplication, and licensing validation.
    """

    def __init__(self):
        self.providers: List[BaseAssetProvider] = [
            WikimediaCommonsProvider(),
            OpenverseProvider(),
            PexelsProvider()
        ]

    async def search(
        self,
        query: str,
        limit: int = 12,
        media_type: str = "image"
    ) -> List[DiscoveredAsset]:
        clean_query = query.strip()
        if not clean_query:
            return []

        # Query active providers
        import asyncio
        tasks = [
            provider.search(clean_query, limit=limit, media_type=media_type)
            for provider in self.providers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined: List[DiscoveredAsset] = []
        for r in results:
            if isinstance(r, list):
                combined.extend(r)

        # Deduplicate by download_url & title
        seen_urls = set()
        deduped: List[DiscoveredAsset] = []
        for a in combined:
            key = a.download_url.strip().lower()
            if key not in seen_urls:
                seen_urls.add(key)
                deduped.append(a)

        # Quality scoring & prioritization
        # Prioritize higher resolution (width * height), valid dimensions, and permissive license
        def quality_score(asset: DiscoveredAsset) -> float:
            score = 100.0
            # Higher resolution
            pixels = asset.width * asset.height
            if pixels >= 1920 * 1080:
                score += 50
            elif pixels >= 1280 * 720:
                score += 30
            # Preferred aspect ratios (landscape ~1.77 or portrait ~0.56)
            if asset.height > 0:
                aspect = asset.width / float(asset.height)
                if abs(aspect - 1.77) < 0.25 or abs(aspect - 0.56) < 0.15:
                    score += 20
            # Provider reliability bonus
            if asset.provider == "wikimedia_commons":
                score += 15
            elif asset.provider == "pexels":
                score += 25
            return score

        deduped.sort(key=quality_score, reverse=True)
        return deduped[:limit]

    # Backward compatibility helper methods
    async def search_wikimedia(self, query: str, limit: int = 10) -> List[DiscoveredAsset]:
        wm = WikimediaCommonsProvider()
        return await wm.search(query, limit=limit, media_type="image")

    async def search_openverse(self, query: str, limit: int = 10) -> List[DiscoveredAsset]:
        ov = OpenverseProvider()
        return await ov.search(query, limit=limit, media_type="image")
