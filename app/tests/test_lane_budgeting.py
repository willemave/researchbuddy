from app.agents.base import LaneSpec, SearchQuery
from app.workflows.review import _allocate_lane_budgets, _allocate_search_query_budgets


def test_allocate_lane_budgets_even_split():
    lanes = [
        LaneSpec(
            name=f"Lane {idx}",
            goal="Test",
            seed_queries=[
                SearchQuery(query="q1", rationale="r"),
                SearchQuery(query="q2", rationale="r"),
            ],
        )
        for idx in range(3)
    ]

    allocated = _allocate_lane_budgets(lanes, max_urls=10)
    budgets = [lane.url_budget for lane in allocated]

    assert sum(budgets) == 10
    assert min(budgets) >= 3
    assert max(budgets) <= 4


def test_allocate_lane_budgets_respects_minimum():
    lanes = [
        LaneSpec(
            name=f"Lane {idx}",
            goal="Test",
            seed_queries=[
                SearchQuery(query="q1", rationale="r"),
                SearchQuery(query="q2", rationale="r"),
            ],
            url_budget=1,
        )
        for idx in range(5)
    ]

    allocated = _allocate_lane_budgets(lanes, max_urls=3)
    budgets = [lane.url_budget for lane in allocated]

    assert sum(budgets) == 5
    assert all(budget >= 1 for budget in budgets)


def test_allocate_search_query_budgets_caps_total_queries() -> None:
    lanes = [
        LaneSpec(
            name=f"Lane {idx}",
            goal="Test",
            seed_queries=[
                SearchQuery(query="q1", rationale="r"),
                SearchQuery(query="q2", rationale="r"),
            ],
            url_budget=idx + 1,
        )
        for idx in range(4)
    ]

    budgets = _allocate_search_query_budgets(lanes, max_search_queries=10)

    assert sum(budgets) == 10
    assert all(budget >= 0 for budget in budgets)
    assert budgets[-1] >= budgets[0]
