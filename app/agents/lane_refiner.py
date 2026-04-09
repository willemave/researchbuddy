"""Lane refinement backed by Codex exec."""

from app.agents.base import AgentDeps, LaneRefinement, SearchQuery
from app.core.settings import get_settings
from app.services.codex_exec import run_codex_prompt
from app.services.research_profiles import ResearchProfile, infer_research_profile
from app.services.semantic_dedupe import QUERY_EMBEDDING_TASK, dedupe_items_by_text
from app.services.usage_tracker import UsageTracker

settings = get_settings()

LANE_REFINER_SYSTEM_PROMPT = (
    "You are refining search queries for a specific research lane. Use the evidence "
    "snippets to propose 6-12 new, high-signal queries that expand coverage. Focus on "
    "evidence gaps, counterpoints, and richer source types. Avoid ecommerce storefronts, "
    "avoid brittle site: filters, and do not repeat existing queries. Overgenerate enough "
    "candidates that a later semantic dedupe pass can remove near-duplicates without losing "
    "distribution."
)


async def refine_lane_queries(
    prompt: str,
    lane_name: str,
    lane_goal: str,
    evidence_snippets: str,
    deps: AgentDeps,
    research_profile: ResearchProfile | None = None,
    usage_tracker: UsageTracker | None = None,
    model_name: str | None = None,
) -> LaneRefinement:
    """Generate follow-up queries for a lane."""

    del deps
    profile = research_profile or infer_research_profile(prompt)
    result, response = await run_codex_prompt(
        (
            f"{LANE_REFINER_SYSTEM_PROMPT}\n\n"
            f"Research mode: {profile.label}\n"
            f"Mode guidance: {profile.refiner_guidance}\n\n"
            "Generate 6-12 new queries for this lane based on evidence.\n"
            "Intentionally spread queries across distinct evidence angles and source types.\n\n"
            f"Prompt: {prompt}\n"
            f"Lane: {lane_name}\n"
            f"Goal: {lane_goal}\n\n"
            f"Evidence:\n{evidence_snippets}"
        ),
        model_name=model_name or settings.refiner_model,
        output_type=LaneRefinement,
    )
    if usage_tracker is not None:
        await usage_tracker.add(response.usage, model_name=model_name or settings.refiner_model)
    return LaneRefinement.model_validate(
        {
            "queries": dedupe_items_by_text(
                result.queries,
                text_getter=lambda query: query.query,
                task_description=QUERY_EMBEDDING_TASK,
                similarity_threshold=settings.semantic_query_similarity_threshold,
                utility_scorer=_query_score,
                max_items=12,
            )
        }
    )


def _query_score(query: SearchQuery) -> float:
    token_count = len({token for token in query.query.lower().split() if token})
    rationale_bonus = min(len(query.rationale.split()), 12)
    return float(token_count + rationale_bonus)
