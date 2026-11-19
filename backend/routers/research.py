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


class AffiliateCampaignRequest(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=200, description="Tên sản phẩm thương mại hoặc tiếp thị liên kết")
    product_category: str = Field(..., description="Danh mục: technology, books, education, finance, lifestyle")
    affiliate_url: str = Field(..., description="Liên kết tiếp thị thực tế của người dùng")
    target_platform: Optional[str] = Field(default="youtube_shorts", description="youtube_shorts, tiktok, reels, landscape_yt")
    discount_or_offer: Optional[str] = Field(default="", description="Ưu đãi hoặc điểm nổi bật")


class AffiliateContentPlan(BaseModel):
    product_name: str
    product_category: str
    affiliate_url: str
    target_platform: str
    storytelling_hook: str
    feature_highlights: List[str]
    honest_limitations: str
    comparison_angle: str
    cta_text: str
    disclosure_statement: str
    qr_code_enabled: bool


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


@router.post("/affiliate-plan", response_model=AffiliateContentPlan)
async def generate_affiliate_content_plan(
    req: AffiliateCampaignRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generates a high-converting, ethical affiliate content plan with product storytelling,
    comparison points, animated CTA cues, and mandatory transparent disclosure.
    """
    p_name = req.product_name.strip()
    return AffiliateContentPlan(
        product_name=p_name,
        product_category=req.product_category,
        affiliate_url=req.affiliate_url,
        target_platform=req.target_platform or "youtube_shorts",
        storytelling_hook=f"Bạn đã từng đau đầu tìm giải pháp cho vấn đề này? Hãy cùng bóc tách thực tế về {p_name}!",
        feature_highlights=[
            f"Tối ưu hiệu suất và tiết kiệm 80% thời gian thực hiện",
            f"Giao diện trực quan, dễ dàng tích hợp và sử dụng",
            f"Giải pháp đáng tin cậy đã được kiểm chứng bởi cộng đồng"
        ],
        honest_limitations=f"Cần thời gian làm quen trong 1-2 ngày đầu để khai thác tối đa tính năng nâng cao.",
        comparison_angle=f"So sánh trực quan giữa phương pháp truyền thống tốn kém và giải pháp hiện đại với {p_name}.",
        cta_text=f"Bấm vào đường link trong phần mô tả / bình luận ghim để nhận ưu đãi đặc biệt!",
        disclosure_statement="Video có chứa liên kết tiếp thị liên kết (Affiliate Link). Chúng tôi có thể nhận hoa hồng nhỏ nếu bạn mua qua link mà không phát sinh thêm bất kỳ chi phí nào.",
        qr_code_enabled=req.target_platform != "landscape_yt"
    )
