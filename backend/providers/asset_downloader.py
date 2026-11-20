import os
import re
import uuid
import socket
import hashlib
import ipaddress
import urllib.parse
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
import httpx
from PIL import Image

from backend.core.config import settings

def is_safe_url(url: str) -> Tuple[bool, str]:
    """
    Validates external media URL to strictly prevent SSRF attacks.
    Rejects private IPs, loopback, link-local, cloud metadata services, and non-HTTP protocols.
    """
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False, "Malformed URL structure"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported URL scheme: {parsed.scheme}. Only HTTP and HTTPS are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in URL"

    hostname_lower = hostname.lower()

    # Reject localhost and suspicious hostnames
    if hostname_lower in ("localhost", "127.0.0.1", "::1", "0.0.0.0", "metadata.google.internal"):
        return False, f"Prohibited host target: {hostname}"

    if hostname_lower.endswith(".local") or hostname_lower.endswith(".internal") or hostname_lower.endswith(".arpa"):
        return False, f"Internal domain target is not permitted: {hostname}"

    # Resolve hostname to IPv4/IPv6 addresses and inspect every resolved IP
    try:
        addr_info = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False, f"Could not resolve host: {hostname}"
    except Exception as e:
        return False, f"DNS resolution failed: {str(e)}"

    if not addr_info:
        return False, f"No IP addresses resolved for host: {hostname}"

    for entry in addr_info:
        ip_str = entry[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private:
                return False, f"Access to private IP range is blocked: {ip_str}"
            if ip.is_loopback:
                return False, f"Access to loopback interface is blocked: {ip_str}"
            if ip.is_link_local:
                return False, f"Access to link-local IP range is blocked: {ip_str}"
            if ip.is_reserved:
                return False, f"Access to reserved IP range is blocked: {ip_str}"
            if ip.is_multicast:
                return False, f"Access to multicast IP range is blocked: {ip_str}"
            if ip.is_unspecified:
                return False, f"Access to unspecified IP range is blocked: {ip_str}"
            # Block AWS/GCP cloud metadata IP explicitly
            if str(ip) == "169.254.169.254":
                return False, "Cloud instance metadata endpoint is strictly prohibited"
        except ValueError:
            return False, f"Invalid IP address format: {ip_str}"

    return True, "URL is safe"

def detect_media_format(header: bytes) -> Optional[str]:
    """Detects MIME format and extension using magic bytes."""
    if len(header) < 12:
        return None

    # JPEG magic bytes: FF D8 FF
    if header.startswith(b"\xFF\xD8\xFF"):
        return "jpg"
    # PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    # WebP magic bytes: RIFF .... WEBP
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "webp"
    # GIF magic bytes: GIF87a or GIF89a
    if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        return "gif"
    # MP4 container: byte 4..8 contains 'ftyp'
    if header[4:8] == b"ftyp":
        return "mp4"

    return None

class AssetDownloaderService:
    """
    Hardened, SSRF-safe streaming asset downloader with magic-byte verification,
    Pillow dimension validation, SHA256 content deduplication, and atomic disk persistence.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        self._custom_storage_dir = storage_dir

    @property
    def storage_dir(self) -> str:
        d = self._custom_storage_dir or getattr(settings, "ASSET_STORAGE_PATH", "./data/assets")
        d_abs = os.path.abspath(d)
        if not os.path.exists(d_abs):
            os.makedirs(d_abs, exist_ok=True)
        return d_abs

    async def download_asset(
        self,
        url: str,
        user_id: str = "system",
        max_size_bytes: Optional[int] = None,
        timeout_sec: Optional[float] = None,
        enforce_animated_policy: bool = False
    ) -> Dict[str, Any]:
        """
        Downloads external media asset securely with SSRF defense, streaming verification,
        and content-based deduplication.
        """
        max_bytes = max_size_bytes or getattr(settings, "MAX_ASSET_SIZE_BYTES", 20 * 1024 * 1024)
        timeout = timeout_sec or getattr(settings, "ASSET_DOWNLOAD_TIMEOUT_SECONDS", 15.0)

        # 1. SSRF Validation
        safe, reason = is_safe_url(url)
        if not safe:
            raise ValueError(f"SSRF Security Violation: {reason}")

        current_url = url
        redirect_limit = 3

        headers = {
            "User-Agent": "YTBerStudio/2.0 (https://github.com/thienduc-07/ytber; contact@ytber.local)",
            "Accept": "image/avif,image/webp,image/apng,image/jpeg,image/png,image/*,video/*;q=0.8"
        }

        # 2. Perform streaming download with hop-by-hop redirect verification
        temp_filename = f"tmp_{uuid.uuid4().hex}.download"
        temp_path = os.path.join(self.storage_dir, temp_filename)

        sha256_hash = hashlib.sha256()
        total_downloaded = 0
        detected_ext = None
        magic_header = bytearray()

        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=False, headers=headers) as client:
                for hop in range(redirect_limit + 1):
                    async with client.stream("GET", current_url) as resp:
                        # Handle redirects securely
                        if resp.status_code in (301, 302, 303, 307, 308):
                            loc = resp.headers.get("Location")
                            if not loc:
                                raise ValueError("Redirect response missing Location header")
                            next_url = urllib.parse.urljoin(current_url, loc)
                            # Re-verify destination URL against SSRF
                            safe_next, next_reason = is_safe_url(next_url)
                            if not safe_next:
                                raise ValueError(f"SSRF Violation on redirect to {next_url}: {next_reason}")
                            current_url = next_url
                            continue

                        if resp.status_code != 200:
                            raise ValueError(f"HTTP download failed with status code {resp.status_code}")

                        # Stream response chunks to disk
                        with open(temp_path, "wb") as f:
                            async for chunk in resp.aiter_bytes(chunk_size=65536):
                                if not chunk:
                                    continue
                                total_downloaded += len(chunk)
                                if total_downloaded > max_bytes:
                                    raise ValueError(f"Tập tin vượt quá dung lượng tối đa cho phép ({max_bytes // (1024*1024)}MB)")

                                sha256_hash.update(chunk)
                                f.write(chunk)

                                if len(magic_header) < 16:
                                    magic_header.extend(chunk[:16 - len(magic_header)])

                        break
                else:
                    raise ValueError("Too many redirects encountered while downloading asset")

            # 3. Magic-Byte Header Verification
            detected_ext = detect_media_format(bytes(magic_header))
            if not detected_ext:
                raise ValueError("Tập tin tải xuống không đúng định dạng hình ảnh/video hợp lệ (Magic bytes mismatch)")

            # 4. Dimension & Integrity Verification via Pillow
            width = 1920
            height = 1080
            media_type = "video" if detected_ext == "mp4" else "image"

            if media_type == "image":
                try:
                    with Image.open(temp_path) as img:
                        img.verify()
                    # Reopen to read dimensions after verify()
                    with Image.open(temp_path) as img:
                        width, height = img.size

                    if enforce_animated_policy:
                        from backend.providers.visual_classifier import AnimatedStyleValidator
                        is_anim, reason, style = AnimatedStyleValidator.validate_image_file(temp_path)
                        if not is_anim:
                            raise ValueError(f"Vi phạm chính sách 100% hình ảnh hoạt hình: {reason}")
                except ValueError:
                    raise
                except Exception as img_err:
                    raise ValueError(f"Tập tin hình ảnh bị lỗi hoặc không thể giải mã: {str(img_err)}")

            # 5. Content-based Deterministic Storage
            hex_digest = sha256_hash.hexdigest()
            final_filename = f"{hex_digest}.{detected_ext}"
            final_path = os.path.join(self.storage_dir, final_filename)

            # Atomic replace or reuse existing
            if os.path.exists(final_path):
                # Clean up temporary file
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            else:
                os.replace(temp_path, final_path)

            return {
                "sha256": hex_digest,
                "filename": final_filename,
                "file_path": final_path,
                "file_size_bytes": total_downloaded,
                "width": width,
                "height": height,
                "media_type": media_type,
                "format": detected_ext,
                "local_url": f"/api/v1/assets/media/{final_filename}"
            }

        except Exception:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise
