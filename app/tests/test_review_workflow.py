import asyncio
import logging
from decimal import Decimal
from pathlib import Path

import pytest

from app.agents.base import AgentDeps, ReviewSynthesis
from app.services.codex_exec import CodexUsage
from app.services.research_profiles import infer_research_profile
from app.services.usage_tracker import UsageSnapshot, UsageTracker
from app.workflows import review


@pytest.mark.asyncio
async def test_synthesize_omits_usage_section_from_markdown(monkeypatch, tmp_path: Path) -> None:
    async def fake_synthesize_review(*args, **kwargs):  # noqa: ANN002, ANN003
        return ReviewSynthesis.model_validate(
            {
                "summary": "Buy model A.",
                "key_findings": ["quiet", "reliable"],
                "recommendation": "Choose model A.",
                "sources": [
                    {"url": "https://example.com", "title": "Review", "notes": "high signal"}
                ],
                "gaps": [],
            }
        )

    monkeypatch.setattr(review, "synthesize_review", fake_synthesize_review)

    usage_tracker = UsageTracker()
    await usage_tracker.add(
        CodexUsage(input_tokens=12, output_tokens=4, requests=1), model_name="gpt-5"
    )

    synthesis_markdown, usage_snapshot = await review._synthesize(
        prompt="best espresso grinder",
        markdown_dir=tmp_path,
        lane_results=[],
        youtube_transcripts=[],
        podcast_transcripts=[],
        deps=AgentDeps(session_id="s", job_id="j"),
        research_profile=infer_research_profile("best espresso grinder"),
        usage_tracker=usage_tracker,
    )

    assert "## Usage" not in synthesis_markdown
    assert "Input tokens:" not in synthesis_markdown
    assert usage_snapshot.total_tokens == 16


def test_search_result_request_size_caps_requested_results(monkeypatch) -> None:
    monkeypatch.setattr(review.settings, "search_num_results", 20)
    monkeypatch.setattr(review.settings, "search_min_results_per_query", 10)

    assert review._search_result_request_size(1) == 10
    assert review._search_result_request_size(5) == 10
    assert review._search_result_request_size(6) == 12
    assert review._search_result_request_size(20) == 20


def test_log_usage_snapshot_includes_search_spend(caplog) -> None:
    snapshot = UsageSnapshot(
        input_tokens=10,
        output_tokens=5,
        requests=2,
        search_requests=3,
        search_requested_results=30,
        search_returned_results=12,
        search_credit_total=Decimal("6"),
        search_cost_total_usd=Decimal("0.024"),
    )

    with caplog.at_level(logging.INFO):
        review._log_usage_snapshot(snapshot)

    assert "Search usage: requests=3 requested_results=30 returned_results=12" in caplog.text
    assert "Search credit total: 6" in caplog.text
    assert "Search spend total: $0.024000" in caplog.text


@pytest.mark.asyncio
async def test_gather_with_limit_caps_concurrency() -> None:
    active = 0
    max_active = 0

    async def worker(value: int) -> int:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        try:
            await asyncio.sleep(0)
            return value
        finally:
            active -= 1

    results = await review._gather_with_limit(  # noqa: SLF001
        [lambda value=value: worker(value) for value in range(6)],
        limit=2,
    )

    assert results == [0, 1, 2, 3, 4, 5]
    assert max_active <= 2
