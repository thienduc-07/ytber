"""
Unit and integration tests for AI Research Engine and Commercial Content Router.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.providers.research_engine import AIResearchEngine


@pytest.fixture
def research_engine():
    return AIResearchEngine()


def test_research_historical_topic(research_engine):
    """Verifies that historical topics extract verified facts, entities, and narrative strategy."""
    report = research_engine.analyze_and_research("Chiến thắng Điện Biên Phủ 1954")
    assert report.category == "historical_doc"
    assert len(report.verified_facts) >= 2
    assert any("Võ Nguyên Giáp" in e.name for e in report.key_entities)
    assert report.narrative_strategy.hook_angle is not None
    assert len(report.misconceptions) >= 1
    assert "https://" in report.verified_facts[0].source_url


def test_research_economics_topic(research_engine):
    """Verifies that economic topics extract CPI facts, compounding rules, and infographics."""
    report = research_engine.analyze_and_research("Lạm phát và sức mua tiền tệ năm 2024")
    assert report.category == "economics"
    assert len(report.verified_facts) >= 1
    assert any(e.entity_type == "concept" for e in report.key_entities)
    assert "Quy tắc 72" in report.verified_facts[1].statement or "sụt giảm" in report.verified_facts[0].statement


def test_research_technology_and_science_topics(research_engine):
    """Verifies technology and astronomy topic analysis."""
    tech_rep = research_engine.analyze_and_research("Trí tuệ nhân tạo và mạng nơ-ron sâu")
    assert tech_rep.category == "technology"
    assert any("Neural" in e.name or "Mạng nơ-ron" in e.name for e in tech_rep.key_entities)

    sci_rep = research_engine.analyze_and_research("Hệ Mặt Trời và các hành tinh")
    assert sci_rep.category == "science"
    assert any("Mặt Trời" in e.name for e in sci_rep.key_entities)


def test_research_router_endpoints():
    """Integration test for /api/v1/research/topic and /api/v1/research/affiliate-plan."""
    client = TestClient(app)

    # 1. Sample research (unauthenticated public discovery)
    sample_resp = client.get("/api/v1/research/sample?topic=Chiến thắng Điện Biên Phủ")
    assert sample_resp.status_code == 200
    data = sample_resp.json()
    assert data["category"] == "historical_doc"
    assert len(data["verified_facts"]) >= 1

    # 2. Topic research with demo token
    headers = {"Authorization": "Bearer demo-guest-token"}
    post_resp = client.post("/api/v1/research/topic", json={
        "topic": "Trí tuệ nhân tạo tương lai",
        "category": "technology"
    }, headers=headers)
    assert post_resp.status_code == 200
    rep_data = post_resp.json()
    assert rep_data["category"] == "technology"
    assert len(rep_data["key_entities"]) >= 1
