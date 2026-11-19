"""
Unit and integration tests for QualityControlEngine.
Verifies container parsing, temporal motion detection, visual style verification, and audio layering.
"""

import os
import tempfile
import subprocess
import pytest
import numpy as np
import cv2
from PIL import Image

from backend.services.quality_control import QualityControlEngine


@pytest.fixture
def sample_animated_video():
    """
    Creates a temporary valid MP4 video with temporal animation and 3-layer audio
    using ffmpeg and synthetic frames.
    """
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "test_animated.mp4")

    # Generate 60 frames (2 seconds at 30fps) of animated vector graphics
    width, height = 360, 640
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_raw_video = os.path.join(temp_dir, "raw_video.mp4")
    out = cv2.VideoWriter(temp_raw_video, fourcc, fps, (width, height))

    for f in range(60):
        t = f / 60.0
        # Draw vector animated style scene
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Gradient sky
        for y in range(height):
            ratio = y / height
            frame[y, :] = [int(150 * ratio), int(80 * (1 - ratio)), int(220 * ratio)]

        # Moving sun / celestial orb (temporal movement)
        sun_x = int(width * (0.3 + 0.4 * t))
        sun_y = int(height * 0.25)
        cv2.circle(frame, (sun_x, sun_y), 30, (255, 220, 100), -1)

        # Vector mountains
        pts = np.array([[0, height], [width // 2, int(height * 0.6)], [width, height]], np.int32)
        cv2.fillPoly(frame, [pts], (40, 25, 60))

        # Moving character / soldier
        char_x = int(width * (0.2 + 0.5 * t))
        char_y = int(height * 0.75)
        cv2.rectangle(frame, (char_x - 15, char_y - 30), (char_x + 15, char_y + 30), (50, 180, 80), -1)
        cv2.circle(frame, (char_x, char_y - 40), 12, (220, 190, 160), -1)

        out.write(frame)
    out.release()

    # Generate synthetic 2s stereo audio with voice + bgm
    sr = 48000
    t_audio = np.linspace(0, 2.0, sr * 2, endpoint=False)
    # Speech tone (400Hz pulse)
    speech = np.sin(2 * np.pi * 440 * t_audio) * 0.3 * (t_audio < 1.4)
    # BGM bass (110Hz continuous bed)
    bgm = np.sin(2 * np.pi * 110 * t_audio) * 0.05
    combined = (speech + bgm).astype(np.float32)

    temp_raw_audio = os.path.join(temp_dir, "raw_audio.raw")
    combined.tofile(temp_raw_audio)

    # Multiplex with ffmpeg to standard H.264 + AAC MP4
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_raw_video,
        "-f", "f32le", "-ar", "48000", "-ac", "1", "-i", temp_raw_audio,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        video_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    yield video_path

    # Cleanup
    for p in [video_path, temp_raw_video, temp_raw_audio]:
        if os.path.exists(p):
            os.remove(p)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


@pytest.fixture
def sample_static_slideshow_video():
    """
    Creates a static video (zero motion across frames) to verify that QualityControlEngine
    strictly rejects slideshows.
    """
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "test_static.mp4")

    width, height = 360, 640
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_raw = os.path.join(temp_dir, "raw_static.mp4")
    out = cv2.VideoWriter(temp_raw, fourcc, fps, (width, height))

    # Single static frame written 60 times
    static_frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.circle(static_frame, (width // 2, height // 2), 50, (200, 200, 200), -1)

    for _ in range(60):
        out.write(static_frame)
    out.release()

    cmd = [
        "ffmpeg", "-y", "-i", temp_raw,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        video_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    yield video_path

    for p in [video_path, temp_raw]:
        if os.path.exists(p):
            os.remove(p)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir)


def test_validate_isobmff_mp4(sample_animated_video):
    """Verifies that ISOBMFF container parser detects ftyp, moov, mdat and stream info."""
    res = QualityControlEngine.validate_isobmff_mp4(sample_animated_video)
    assert res["passed"] is True
    assert res["has_ftyp"] is True
    assert res["has_moov"] is True
    assert res["has_mdat"] is True
    assert res["video_stream"]["valid"] is True
    assert res["video_stream"]["fps"] > 0
    assert res["video_stream"]["frame_count"] >= 50


def test_validate_temporal_motion_success(sample_animated_video):
    """Verifies that non-zero temporal movement is recognized and passes."""
    res = QualityControlEngine.validate_temporal_motion(sample_animated_video, sample_step=5)
    assert res["passed"] is True
    assert res["mean_motion_delta"] > 0.002
    assert "Genuine Temporal Motion" in res["verdict"]


def test_validate_temporal_motion_rejects_static_slideshow(sample_static_slideshow_video):
    """Verifies that static slideshows fail the temporal motion check."""
    res = QualityControlEngine.validate_temporal_motion(sample_static_slideshow_video, sample_step=5)
    assert res["passed"] is False
    assert res["mean_motion_delta"] < 0.001
    assert "Static Slideshow Detected" in res["verdict"]


def test_validate_animated_visual_policy(sample_animated_video):
    """Verifies that vector/animated stylization satisfies 100% animated policy."""
    res = QualityControlEngine.validate_animated_visual_policy(sample_animated_video, num_samples=5)
    assert res["passed"] is True
    assert res["compliance_ratio"] >= 0.80
    assert "100% Animated Visual Policy Verified" in res["verdict"]


def test_validate_three_layer_audio(sample_animated_video):
    """Verifies that audio track with voice activity and background bed is recognized."""
    res = QualityControlEngine.validate_three_layer_audio(sample_animated_video)
    assert res["passed"] is True
    assert res["has_voice_activity"] is True
    assert res["has_bgm_bed"] is True
    assert res["rms_energy"] > 0.01


def test_run_full_aqc(sample_animated_video):
    """Verifies end-to-end AQC report on a valid animated short."""
    report = QualityControlEngine.run_full_aqc(sample_animated_video)
    assert report["overall_passed"] is True
    assert report["container_check"]["passed"] is True
    assert report["temporal_motion_check"]["passed"] is True
    assert report["animated_policy_check"]["passed"] is True
    assert report["audio_layers_check"]["passed"] is True
    assert "PASSED" in report["summary_verdict"]
