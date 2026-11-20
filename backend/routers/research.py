"""
Research & Commercial Content Router.
Provides AI content intelligence, fact verification, narrative strategy,
and affiliate monetization metadata.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field

from backend.core.security import get_current_user_id
from backend.providers.research_engine import AIResearchEngine, TopicResearchReport

router = APIRouter(prefix="/api/v1/research", tags=["AI Research & Content Intelligence"])
research_engine = AIResearchEngine()


class TopicResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=1000, description="Chủ đề hoặc ý tưởng kịch bản cần nghiên cứu")
    category: Optional[str] = Field(default="general", description="historical_doc, economics, technology, science, environment, business, education")


@router.post("/topic", response_model=TopicResearchReport)
async def research_topic_endpoint(
    req: TopicResearchRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Analyzes and researches a topic or script idea before video production.
    Extracts verified facts, reputable source citations, key entities with 2.5D visual directives,
    misconceptions, and high-retention narrative strategy.
    """
    try:
        report = research_engine.analyze_and_research(
            topic=req.topic,
            category_override=req.category
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research analysis failed: {str(e)}"
        )


@router.get("/sample", response_model=TopicResearchReport)
async def get_sample_research(
    topic: Optional[str] = Query(default="Chiến thắng Điện Biên Phủ 1954"),
    category: Optional[str] = Query(default="historical_doc")
):
    """Returns instant sample research dossier for studio onboarding."""
    return research_engine.analyze_and_research(topic=topic, category_override=category)
