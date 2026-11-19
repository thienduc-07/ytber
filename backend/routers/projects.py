import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import get_current_user_id
from backend.core.database import get_db
from backend.models.db_models import ProjectModel, EpisodeModel, ChapterModel

router = APIRouter(prefix="/api/v1/projects", tags=["Project & Episode Management"])

class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default="")
    video_type: Optional[str] = Field(default="short-form", pattern="^(short-form|long-form)$")
    genre: Optional[str] = Field(default="general")

class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|ready|rendering|completed)$")
    genre: Optional[str] = None
    video_type: Optional[str] = Field(None, pattern="^(short-form|long-form)$")

class EpisodeCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    script_raw: str = Field(default="")
    voice_config: Optional[Dict[str, Any]] = Field(default_factory=lambda: {
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+0%",
        "pitch": "+0Hz"
    })
    video_specs: Optional[Dict[str, Any]] = None

class ChapterCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    chapter_order: int = Field(default=1)
    summary: Optional[str] = ""
    duration_seconds: Optional[float] = 60.0

class ManifestUpdateRequest(BaseModel):
    manifest_json: Dict[str, Any]

@router.get("", response_model=List[Dict[str, Any]])
async def list_user_projects(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List all projects belonging to the authenticated user from persistent storage."""
    stmt = select(ProjectModel).where(ProjectModel.user_id == user_id).order_by(ProjectModel.updated_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return [p.to_dict() for p in projects]

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_project(
    req: ProjectCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project isolated to the authenticated user."""
    proj_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    new_proj = ProjectModel(
        id=proj_id,
        user_id=user_id,
        title=req.title,
        description=req.description or "",
        status="draft",
        video_type=req.video_type or "short-form",
        genre=req.genre or "general",
        created_at=now,
        updated_at=now,
    )
    db.add(new_proj)
    await db.commit()
    await db.refresh(new_proj)
    return new_proj.to_dict()

@router.get("/{project_id}", response_model=Dict[str, Any])
async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve details for a specific project ensuring tenant isolation."""
    stmt = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.execute(stmt)
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if proj.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")
    return proj.to_dict()

@router.put("/{project_id}", response_model=Dict[str, Any])
async def update_project(
    project_id: str,
    req: ProjectUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update project metadata in persistent storage."""
    stmt = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.execute(stmt)
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if proj.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")
    
    if req.title is not None:
        proj.title = req.title
    if req.description is not None:
        proj.description = req.description
    if req.status is not None:
        proj.status = req.status
    if req.genre is not None:
        proj.genre = req.genre
    if req.video_type is not None:
        proj.video_type = req.video_type
        
    proj.updated_at = datetime.utcnow().isoformat() + "Z"
    await db.commit()
    await db.refresh(proj)
    return proj.to_dict()

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project and all associated episodes and chapters."""
    stmt = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.execute(stmt)
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if proj.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")
    
    await db.delete(proj)
    await db.commit()
    return None

# Episode endpoints
@router.get("/{project_id}/episodes", response_model=List[Dict[str, Any]])
async def list_project_episodes(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List all episodes in a project."""
    stmt = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.execute(stmt)
    proj = result.scalar_one_or_none()
    if not proj or proj.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    ep_stmt = select(EpisodeModel).where(EpisodeModel.project_id == project_id).order_by(EpisodeModel.created_at.desc())
    ep_result = await db.execute(ep_stmt)
    episodes = ep_result.scalars().all()
    return [e.to_dict() for e in episodes]

@router.post("/{project_id}/episodes", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_episode(
    project_id: str,
    req: EpisodeCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new episode in a project with default specs matching project type."""
    stmt = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await db.execute(stmt)
    proj = result.scalar_one_or_none()
    if not proj or proj.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    ep_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    
    default_specs = (
        {"width": 1920, "height": 1080, "fps": 30}
        if proj.video_type == "long-form"
        else {"width": 1080, "height": 1920, "fps": 30}
    )
    
    new_ep = EpisodeModel(
        id=ep_id,
        project_id=project_id,
        user_id=user_id,
        title=req.title,
        script_raw=req.script_raw or "",
        voice_config=req.voice_config or {"voice": "vi-VN-NamMinhNeural", "rate": "+0%", "pitch": "+0Hz"},
        video_specs=req.video_specs or default_specs,
        audio_specs={"target_lufs": -14.0, "true_peak": -1.0},
        manifest_json=None,
        status="draft",
        created_at=now,
        updated_at=now,
    )
    db.add(new_ep)
    await db.commit()
    await db.refresh(new_ep)
    return new_ep.to_dict()

# Manifest & Chapter endpoints (under /api/v1/episodes)
episode_manifest_router = APIRouter(prefix="/api/v1/episodes", tags=["Episode Manifest & Chapters"])

@episode_manifest_router.get("/{episode_id}", response_model=Dict[str, Any])
async def get_episode_detail(
    episode_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get single episode with its manifest."""
    stmt = select(EpisodeModel).where(EpisodeModel.id == episode_id)
    result = await db.execute(stmt)
    ep = result.scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    if ep.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return ep.to_dict()

@episode_manifest_router.put("/{episode_id}/manifest", response_model=Dict[str, Any])
async def update_episode_manifest(
    episode_id: str,
    req: ManifestUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Save or update scene manifest for an episode."""
    stmt = select(EpisodeModel).where(EpisodeModel.id == episode_id)
    result = await db.execute(stmt)
    ep = result.scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    if ep.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    ep.manifest_json = req.manifest_json
    ep.status = "analyzed"
    ep.updated_at = datetime.utcnow().isoformat() + "Z"
    await db.commit()
    await db.refresh(ep)
    return ep.to_dict()

@episode_manifest_router.get("/{episode_id}/chapters", response_model=List[Dict[str, Any]])
async def list_episode_chapters(
    episode_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List chapters belonging to a long-form episode."""
    stmt = select(EpisodeModel).where(EpisodeModel.id == episode_id)
    result = await db.execute(stmt)
    ep = result.scalar_one_or_none()
    if not ep or ep.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")

    ch_stmt = select(ChapterModel).where(ChapterModel.episode_id == episode_id).order_by(ChapterModel.chapter_order.asc())
    ch_res = await db.execute(ch_stmt)
    chapters = ch_res.scalars().all()
    return [c.to_dict() for c in chapters]

@episode_manifest_router.post("/{episode_id}/chapters", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_episode_chapter(
    episode_id: str,
    req: ChapterCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Add a chapter to a long-form episode."""
    stmt = select(EpisodeModel).where(EpisodeModel.id == episode_id)
    result = await db.execute(stmt)
    ep = result.scalar_one_or_none()
    if not ep or ep.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")

    chapter = ChapterModel(
        id=str(uuid.uuid4()),
        episode_id=episode_id,
        user_id=user_id,
        chapter_order=req.chapter_order,
        title=req.title,
        summary=req.summary or "",
        duration_seconds=req.duration_seconds or 60.0,
        status="pending",
        created_at=datetime.utcnow().isoformat() + "Z",
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    return chapter.to_dict()
