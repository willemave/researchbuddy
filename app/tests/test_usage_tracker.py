import asyncio
from decimal import Decimal

from app.models.review import SearchUsage
from app.services.codex_exec import CodexUsage
from app.services.usage_tracker import UsageTracker


def test_usage_tracker_aggregates() -> None:
    tracker = UsageTracker()

    async def _run() -> None:
        await tracker.add(
            CodexUsage(input_tokens=10, output_tokens=5, requests=1), model_name="gpt-5.4"
        )
        await tracker.add(
            CodexUsage(input_tokens=3, output_tokens=7, requests=2), model_name="gpt-5.4"
        )
        await tracker.add_source("reddit", count=2)
        await tracker.add_source("youtube")
        await tracker.add_search_usage(
            SearchUsage(
                provider_name="exa",
                requested_results=10,
                returned_results=1,
                cost_amount_usd=Decimal("0.007"),
            )
        )
        await tracker.add_search_usage(
            SearchUsage(
                provider_name="exa",
                requested_results=10,
                returned_results=2,
                cost_amount_usd=Decimal("0.007"),
            )
        )
        snapshot = await tracker.snapshot(include_costs=True)
        assert snapshot.input_tokens == 13
        assert snapshot.output_tokens == 12
        assert snapshot.requests == 3
        assert snapshot.total_tokens == 25
        assert snapshot.sources["reddit"] == 2
        assert snapshot.sources["youtube"] == 1
        assert snapshot.per_model["gpt-5.4"].input_tokens == 13
        assert snapshot.search_requests == 2
        assert snapshot.search_requested_results == 20
        assert snapshot.search_returned_results == 3
        assert snapshot.search_cost_total_usd == Decimal("0.014")
        assert snapshot.search_usage_by_provider["exa"].cost_total_usd == Decimal("0.014")

    asyncio.run(_run())
