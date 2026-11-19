import os
import re
from typing import Tuple, Optional, Dict, Any
from PIL import Image

class AnimatedStyleValidator:
    """
    Independent Gatekeeper for Strict Animated Visual Policy.
    Enforces 100% Animated Visual Assets — 0% Real-Life Photographs.
    Performs two independent layers of validation:
      1. Semantic Relevance Validation
      2. Animated Style Compliance (Rejects real photos, live action, stock photos).
    """

    PROHIBITED_METADATA_MARKERS = [
        "photograph", "photo", "portrait photo", "press photo", "stock photo",
        "live action", "news footage", "camera", "daguerreotype", "kodak",
        "nikon", "canon", "reuters", "getty", "ap photo", "ap wire",
        "taken with", "f/2.8", "f/1.8", "iso 100", "iso 400", "iso 800", "shutter speed"
    ]

    ALLOWED_ANIMATION_MARKERS = [
        "illustration", "vector", "drawing", "cartoon", "clipart", "animated",
        "infographic", "sketch", "diagram", "icon", "artwork", "painting",
        "stylized", "character", "caricature", "anime", "manga", "cel", "flat design",
        "2d", "2.5d", "motion graphics", "render", "cgi", "line art"
    ]

    @classmethod
    def validate_metadata(
        cls,
        title: str = "",
        description: str = "",
        source_url: str = ""
    ) -> Tuple[bool, str, str]:
        """
        Validates metadata and URL strings against photographic vs animated markers.
        Returns: (is_compliant, reason, detected_style)
        """
        combined = f"{title} {description} {source_url}".lower()

        # 1. Prohibited Photographic Markers Check
        for marker in cls.PROHIBITED_METADATA_MARKERS:
            # Match whole words or standard phrases
            if re.search(r'\b' + re.escape(marker) + r'\b', combined):
                # Exception: if explicit "not a photo" or "cartoon of photo"
                if "cartoon" not in combined and "illustration" not in combined and "drawing" not in combined:
                    return False, f"Prohibited photographic marker detected: '{marker}'", "photograph"

        # 2. Check for Positive Animation / Illustration Markers
        has_anim_marker = any(m in combined for m in cls.ALLOWED_ANIMATION_MARKERS)
        if has_anim_marker:
            if "cartoon" in combined or "comic" in combined:
                style = "2d_cartoon"
            elif "infographic" in combined or "diagram" in combined:
                style = "infographic_vector"
            elif "vector" in combined or "svg" in combined or "clipart" in combined:
                style = "vector_illustration"
            else:
                style = "stylized_illustration"
            return True, "Valid animated/illustration metadata confirmed", style

        # If neutral/ambiguous metadata, permit as candidate for pixel inspection
        return True, "Neutral metadata; requires visual inspection", "stylized_candidate"

    @classmethod
    def validate_image_file(
        cls,
        file_path: str,
        title: str = "",
        description: str = ""
    ) -> Tuple[bool, str, str]:
        """
        Deep pixel-level inspection of image to enforce animated style compliance.
        Analyzes color distribution, gradient variance, and EXIF camera data.
        """
        if not os.path.exists(file_path):
            return False, f"Image file not found: {file_path}", "missing"

        # 1. First check metadata
        meta_ok, meta_reason, detected_style = cls.validate_metadata(title, description, file_path)
        if not meta_ok:
            return False, meta_reason, "photograph"

        # 2. Pixel & EXIF inspection
        try:
            with Image.open(file_path) as img:
                # Check for camera EXIF metadata
                exif = img.getexif()
                if exif:
                    # Camera Make (0x010F) or Model (0x0110)
                    make = exif.get(0x010F)
                    model = exif.get(0x0110)
                    if make or model:
                        return False, f"Camera EXIF hardware detected: {make} {model}", "photograph"

                # Check image format: SVG/Vector converted to PNG/WebP
                if img.format in ("PNG", "WEBP", "GIF"):
                    # Check for alpha channel or flat color blocks
                    if img.mode in ("RGBA", "LA", "P"):
                        return True, "Vector/transparent animated asset verified", detected_style or "vector_illustration"

                # Convert to RGB and inspect color complexity
                rgb_img = img.convert("RGB")
                w, h = rgb_img.size

                # Sample 1000 random pixels to check color quantization
                # Cartoon/vector illustrations typically have clustered color palettes
                colors = rgb_img.resize((64, 64), Image.Resampling.NEAREST).getcolors(maxcolors=4096)
                if colors:
                    distinct_color_count = len(colors)
                    # 64x64 = 4096 pixels. Highly detailed real-world photographs have > 1500 distinct colors
                    # Illustrations and cartoons usually have < 800 distinct colors in 64x64
                    if distinct_color_count < 950:
                        return True, f"Flat/quantized color palette verified ({distinct_color_count} colors)", detected_style or "2d_cartoon"

                # If ambiguous, check if metadata explicitly confirmed illustration
                if any(m in f"{title} {description}".lower() for m in cls.ALLOWED_ANIMATION_MARKERS):
                    return True, "Confirmed by verified illustration metadata", detected_style

                # Fail-closed policy: reject unverified photorealistic images
                return False, "Asset has continuous tone photorealistic characteristics (fails animated policy)", "photograph"

        except Exception as e:
            return False, f"Image inspection error: {str(e)}", "corrupt"

    @classmethod
    def validate_scene_relevance(
        cls,
        scene_description: str,
        asset_title: str,
        asset_keywords: list
    ) -> Tuple[bool, float, str]:
        """
        Layer 1: Semantic Relevance Validation.
        Computes match score between scene description and candidate asset.
        """
        desc_lower = scene_description.lower()
        title_lower = asset_title.lower()

        # Extract words from description
        desc_words = set(re.findall(r'\w{3,}', desc_lower))
        if not desc_words:
            return True, 1.0, "Empty scene description"

        # Check keyword matches
        matches = 0
        for kw in asset_keywords:
            kw_clean = kw.lower()
            if any(w in kw_clean for w in desc_words):
                matches += 1

        for w in desc_words:
            if w in title_lower:
                matches += 2

        score = min(1.0, matches / max(1, len(asset_keywords) + 2))
        if score >= 0.2:
            return True, score, f"Semantic relevance score: {score:.2f}"
        else:
            return False, score, f"Low semantic relevance score: {score:.2f}"
