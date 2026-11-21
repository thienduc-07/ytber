import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Integer, Float, Text, JSON, ForeignKey, Index, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    status = Column(String(32), default="draft")
    video_type = Column(String(32), default="short-form")  # "short-form" or "long-form"
    genre = Column(String(64), default="general")
    created_at = Column(String(32), default=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at = Column(String(32), default=lambda: datetime.utcnow().isoformat() + "Z")

    episodes = relationship("EpisodeModel", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "video_type": self.video_type,
            "genre": self.genre,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class EpisodeModel(Base):
    __tablename__ = "episodes"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    script_raw = Column(Text, default="")
    voice_config = Column(JSON, default=dict)
    video_specs = Column(JSON, default=dict)
    audio_specs = Column(JSON, default=dict)
    manifest_json = Column(JSON, nullable=True)
    status = Column(String(32), default="draft")
    created_at = Column(String(32), default=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at = Column(String(32), default=lambda: datetime.utcnow().isoformat() + "Z")

    project = relationship("ProjectModel", back_populates="episodes")
    chapters = relationship("ChapterModel", back_populates="episode", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "title": self.title,
            "script_raw": self.script_raw,
            "voice_config": self.voice_config or {},
            "video_specs": self.video_specs or {},
            "audio_specs": self.audio_specs or {},
            "manifest_json": self.manifest_json,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class ChapterModel(Base):
    __tablename__ = "chapters"

    id = Column(String(36), primary_key=True)
    episode_id = Column(String(36), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    chapter_order = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, default="")
    duration_seconds = Column(Float, default=0.0)
    status = Column(String(32), default="pending")
    created_at = Column(String(32), default=lambda: datetime.utcnow().isoformat() + "Z")

    episode = relationship("EpisodeModel", back_populates="chapters")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "episode_id": self.episode_id,
            "user_id": self.user_id,
            "chapter_order": self.chapter_order,
            "title": self.title,
            "summary": self.summary,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "created_at": self.created_at,
        }
class RenderJobModel(Base):
    __tablename__ = "render_jobs"

    id = Column(String(36), primary_key=True)
    episode_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    job_type = Column(String(32), default="shorts")
    status = Column(String(32), default="pending")  # pending, queued, building_composition, rendering_mp4, validating, completed, failed, cancelled
    progress = Column(Integer, default=0)
    stage_text = Column(String(255), default="Đang chờ xếp hàng...")
    output_url = Column(String(512), nullable=True)
    output_mp4_path = Column(String(512), nullable=True)
    duration_seconds = Column(Float, default=0.0)
    file_size_bytes = Column(Integer, default=0)
    resolution = Column(String(32), default="1080x1920")
    video_format = Column(String(32), default="short-form")
    manifest_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(String(32), default=lambda: datetime.utcnow().isoformat() + "Z")
    completed_at = Column(String(32), nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "episode_id": self.episode_id,
            "user_id": self.user_id,
            "job_type": self.job_type,
            "status": self.status,
            "progress": self.progress,
            "stage_text": self.stage_text,
            "output_url": self.output_url,
            "output_mp4_path": self.output_mp4_path,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "resolution": self.resolution,
            "video_format": self.video_format,
            "manifest_json": self.manifest_json,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

class AudioFileModel(Base):
    __tablename__ = "audio_files"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    filename = Column(String(255), nullable=False, index=True)
    duration_seconds = Column(Float, default=0.0)
    created_at = Column(String(32), default=lambda: datetime.utcnow().isoformat() + "Z")

    __table_args__ = (
        Index("idx_audio_filename_user", "filename", "user_id", unique=True),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at,
        }
class AssetModel(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    sha256 = Column(String(64), nullable=False, index=True)
    filename = Column(String(255), nullable=False, index=True)
    provider = Column(String(64), default="unknown")
    source_url = Column(String(1024), default="")
    media_type = Column(String(32), default="image")
    title = Column(String(255), default="")
    creator = Column(String(255), default="")
    license_type = Column(String(128), default="")
    license_url = Column(String(512), default="")
    attribution_required = Column(Boolean, default=True)
    attribution_text = Column(Text, default="")
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    created_at = Column(String(32), default=lambda: datetime.utcnow().isoformat() + "Z")

    __table_args__ = (
        Index("idx_asset_filename_user", "filename", "user_id", unique=True),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sha256": self.sha256,
            "filename": self.filename,
            "provider": self.provider,
            "source_url": self.source_url,
            "media_type": self.media_type,
            "title": self.title,
            "creator": self.creator,
            "license_type": self.license_type,
            "license_url": self.license_url,
            "attribution_required": self.attribution_required,
            "attribution_text": self.attribution_text,
            "width": self.width,
            "height": self.height,
            "file_size_bytes": self.file_size_bytes,
            "created_at": self.created_at,
        }
