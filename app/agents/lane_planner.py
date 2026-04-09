"""Lane planner backed by Codex exec."""

from app.agents.base import AgentDeps, LanePlan, LaneSpec, SearchQuery
from app.core.settings import get_settings
from app.services.codex_exec import run_codex_prompt
from app.services.research_profiles import ResearchProfile, infer_research_profile
from app.services.semantic_dedupe import (
    LANE_EMBEDDING_TASK,
    QUERY_EMBEDDING_TASK,
    cluster_texts_by_similarity,
    dedupe_items_by_text,
)
from app.services.usage_tracker import UsageTracker

settings = get_settings()

LANE_PLANNER_SYSTEM_PROMPT = (
    "You are a research planner. Break the user's prompt into 5-10 independent "
    "research lanes that can run in parallel. Each lane must include a short name, "
    "a clear goal, and 4-8 seed search queries. Lanes should cover source diversity, "
    "competing viewpoints, first-hand experience, expert analysis, and unresolved gaps. "
    "Avoid ecommerce/storefront pages unless they contribute unique primary information. "
    "Prefer natural-language queries over brittle site: filters. Overgenerate enough query "
    "coverage that a later dedupe pass can remove near-duplicates without collapsing search "
    "distribution."
)


async def plan_lanes(
    prompt: str,
    deps: AgentDeps,
    research_profile: ResearchProfile | None = None,
    usage_tracker: UsageTracker | None = None,
    model_name: str | None = None,
) -> LanePlan:
    """Plan research lanes for the given prompt."""

    del deps
    profile = research_profile or infer_research_profile(prompt)
    result, response = await run_codex_prompt(
        (
            f"{LANE_PLANNER_SYSTEM_PROMPT}\n\n"
            f"Research mode: {profile.label}\n"
            f"Mode guidance: {profile.planner_guidance}\n\n"
            "Design research lanes for this request. Provide 4-8 seed queries per lane.\n"
            "Queries inside a lane must intentionally span distinct evidence angles such as "
            "hands-on reviews, complaints, comparisons, benchmarks, alternatives, and edge cases.\n\n"
            f"Prompt: {prompt}"
        ),
        model_name=model_name or settings.planner_model,
        output_type=LanePlan,
    )
    if usage_tracker is not None:
        await usage_tracker.add(response.usage, model_name=model_name or settings.planner_model)
    return _postprocess_lane_plan(result)


def _postprocess_lane_plan(plan: LanePlan) -> LanePlan:
    lanes = [_normalize_lane_queries(lane) for lane in plan.lanes]
    lane_clusters = cluster_texts_by_similarity(
        [_lane_text(lane) for lane in lanes],
        task_description=LANE_EMBEDDING_TASK,
        similarity_threshold=settings.semantic_lane_similarity_threshold,
    )

    merged_lanes: list[LaneSpec] = []
    for cluster in lane_clusters:
        merged_lane = _merge_lane_cluster([lanes[idx] for idx in cluster])
        merged_lanes.append(merged_lane)

    if len(merged_lanes) < 3:
        for lane in lanes:
            if any(existing.name == lane.name and existing.goal == lane.goal for existing in merged_lanes):
                continue
            merged_lanes.append(lane)
            if len(merged_lanes) >= 3:
                break

    return LanePlan.model_validate({"lanes": merged_lanes[:12]})


def _merge_lane_cluster(cluster: list[LaneSpec]) -> LaneSpec:
    primary = max(cluster, key=lambda lane: (_lane_score(lane), -len(lane.goal)))
    combined_queries: list[SearchQuery] = []
    for lane in cluster:
        combined_queries.extend(lane.seed_queries)
    deduped_queries = _dedupe_queries(combined_queries, max_queries=10)
    return primary.model_copy(
        update={
            "seed_queries": deduped_queries,
            "url_budget": max((lane.url_budget or 0) for lane in cluster) or None,
        }
    )


def _normalize_lane_queries(lane: LaneSpec) -> LaneSpec:
    return lane.model_copy(update={"seed_queries": _dedupe_queries(lane.seed_queries, max_queries=10)})


def _dedupe_queries(queries: list[SearchQuery], *, max_queries: int) -> list[SearchQuery]:
    deduped = dedupe_items_by_text(
        queries,
        text_getter=lambda query: query.query,
        task_description=QUERY_EMBEDDING_TASK,
        similarity_threshold=settings.semantic_query_similarity_threshold,
        utility_scorer=_query_score,
        max_items=max_queries,
    )
    if len(deduped) >= 2:
        return deduped

    for query in queries:
        if any(existing.query == query.query for existing in deduped):
            continue
        deduped.append(query)
        if len(deduped) >= 2:
            break
    return deduped[:max_queries]


def _lane_text(lane: LaneSpec) -> str:
    return f"{lane.name}\n{lane.goal}"


def _lane_score(lane: LaneSpec) -> float:
    return float((lane.url_budget or 0) * 10) + float(len(lane.seed_queries))


def _query_score(query: SearchQuery) -> float:
    token_count = len({token for token in query.query.lower().split() if token})
    rationale_bonus = min(len(query.rationale.split()), 12)
    return float(token_count + rationale_bonus)
