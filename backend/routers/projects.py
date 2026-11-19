from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from backend.core.security import get_current_user_id

router = APIRouter(prefix="/api/v1/projects", tags=["Project & Episode Management"])

# In-memory store for backend API state and mock/test runs
# Keyed by project_id / episode_id
_PROJECTS_STORE: Dict[str, Dict[str, Any]] = {}
_EPISODES_STORE: Dict[str, Dict[str, Any]] = {}

class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default="")

class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|ready|rendering|completed)$")

class EpisodeCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    script_raw: str = Field(default="")
    voice_config: Optional[Dict[str, Any]] = Field(default_factory=lambda: {
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+0%",
        "pitch": "+0Hz"
    })

class ManifestUpdateRequest(BaseModel):
    manifest_json: Dict[str, Any]

@router.get("", response_model=List[Dict[str, Any]])
async def list_user_projects(user_id: str = Depends(get_current_user_id)):
    """List all projects belonging to the authenticated user."""
    user_projs = [
        p for p in _PROJECTS_STORE.values()
        if p.get("user_id") == user_id
    ]
    user_projs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return user_projs

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_project(
    req: ProjectCreateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new project isolated to the authenticated user."""
    proj_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    new_proj = {
        "id": proj_id,
        "user_id": user_id,
        "title": req.title,
        "description": req.description,
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    _PROJECTS_STORE[proj_id] = new_proj
    return new_proj

@router.get("/{project_id}", response_model=Dict[str, Any])
async def get_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Retrieve details for a specific project ensuring tenant isolation."""
    proj = _PROJECTS_STORE.get(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if proj.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")
    return proj

@router.put("/{project_id}", response_model=Dict[str, Any])
async def update_project(
    project_id: str,
    req: ProjectUpdateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Update project metadata."""
    proj = _PROJECTS_STORE.get(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if proj.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")
    
    if req.title is not None:
        proj["title"] = req.title
    if req.description is not None:
        proj["description"] = req.description
    if req.status is not None:
        proj["status"] = req.status
    proj["updated_at"] = datetime.utcnow().isoformat() + "Z"

    _PROJECTS_STORE[project_id] = proj
    return proj

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a project and all associated episodes."""
    proj = _PROJECTS_STORE.get(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if proj.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")
    
    # Delete associated episodes
    ep_ids = [eid for eid, ep in _EPISODES_STORE.items() if ep.get("project_id") == project_id]
    for eid in ep_ids:
        _EPISODES_STORE.pop(eid, None)

    _PROJECTS_STORE.pop(project_id, None)
    return None

# Episode endpoints
@router.get("/{project_id}/episodes", response_model=List[Dict[str, Any]])
async def list_project_episodes(
    project_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """List all episodes in a project."""
    proj = _PROJECTS_STORE.get(project_id)
    if not proj or proj.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    episodes = [
        ep for ep in _EPISODES_STORE.values()
        if ep.get("project_id") == project_id
    ]
    return episodes

@router.post("/{project_id}/episodes", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_episode(
    project_id: str,
    req: EpisodeCreateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new episode in a project."""
    proj = _PROJECTS_STORE.get(project_id)
    if not proj or proj.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    ep_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    new_ep = {
        "id": ep_id,
        "project_id": project_id,
        "user_id": user_id,
        "title": req.title,
        "script_raw": req.script_raw,
        "voice_config": req.voice_config,
        "video_specs": {"width": 1080, "height": 1920, "fps": 30},
        "audio_specs": {"target_lufs": -14.0, "true_peak": -1.0},
        "manifest_json": None,
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    _EPISODES_STORE[ep_id] = new_ep
    return new_ep

# Manifest endpoints (under /api/v1/episodes)
episode_manifest_router = APIRouter(prefix="/api/v1/episodes", tags=["Episode Manifest"])

@episode_manifest_router.get("/{episode_id}", response_model=Dict[str, Any])
async def get_episode_detail(
    episode_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get single episode with its manifest."""
    ep = _EPISODES_STORE.get(episode_id)
    if not ep:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    if ep.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return ep

@episode_manifest_router.put("/{episode_id}/manifest", response_model=Dict[str, Any])
async def update_episode_manifest(
    episode_id: str,
    req: ManifestUpdateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Save or update scene manifest for an episode."""
    ep = _EPISODES_STORE.get(episode_id)
    if not ep:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    if ep.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    ep["manifest_json"] = req.manifest_json
    ep["status"] = "analyzed"
    ep["updated_at"] = datetime.utcnow().isoformat() + "Z"
    _EPISODES_STORE[episode_id] = ep
    return ep
