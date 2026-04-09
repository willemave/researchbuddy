"""Research intent inference and source preferences."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel

ResearchMode = Literal["product_review", "restaurant_recommendation", "general_research"]
ResearchModeOption = Literal["auto", "product", "restaurant", "research"]

RESTAURANT_KEYWORDS = (
    "restaurant",
    "restaurants",
    "dining",
    "where to eat",
    "food",
    "brunch",
    "dinner",
    "lunch",
    "breakfast",
    "tasting menu",
    "omakase",
    "pizza",
    "burger",
    "sushi",
    "taco",
    "tacos",
    "barbecue",
    "bbq",
    "coffee shop",
    "cafe",
    "cafes",
    "cocktail bar",
    "wine bar",
    "steakhouse",
)
PRODUCT_KEYWORDS = (
    "review",
    "reviews",
    "vs",
    "versus",
    "worth it",
    "buy",
    "purchase",
    "hands on",
    "hands-on",
    "comparison",
    "compare",
    "best",
    "top",
    "quietest",
    "durability",
    "battery life",
    "reliability",
    "model",
    "version",
    "spec",
    "specs",
)
GENERAL_RESEARCH_HINTS = (
    "research",
    "overview",
    "explain",
    "history",
    "trend",
    "topic",
    "industry",
    "market",
    "policy",
)


class ResearchProfile(BaseModel):
    """Runtime research preferences inferred from the prompt."""

    mode: ResearchMode
    label: str
    planner_guidance: str
    refiner_guidance: str
    synthesis_guidance: str
    query_suffix: str
    preferred_source_kinds: tuple[str, ...]
    discouraged_source_kinds: tuple[str, ...]
    youtube_results: int
    podcast_results: int


def infer_research_profile(prompt: str) -> ResearchProfile:
    """Infer the research profile for a prompt."""

    lowered = prompt.lower()

    if _matches_any(lowered, RESTAURANT_KEYWORDS):
        return ResearchProfile(
            mode="restaurant_recommendation",
            label="Restaurant Recommendations",
            planner_guidance=(
                "Treat this as a restaurant recommendation task. Prioritize local magazines, "
                "city guides, neighborhood food publications, Reddit, Chowhound-style forums, "
                "and first-hand diner reports. Avoid generic SEO listicles. YouTube is low-priority "
                "unless the prompt explicitly asks for it."
            ),
            refiner_guidance=(
                "Bias new queries toward local publications, neighborhood discussions, Reddit, "
                "food forums, and menu-specific diner feedback. Avoid generic roundup phrasing "
                "and keep YouTube as a fallback only."
            ),
            synthesis_guidance=(
                "Answer as a recommendation brief. Surface atmosphere, signature dishes, pricing "
                "signals, neighborhood fit, and consensus or disagreement across locals."
            ),
            query_suffix='"local magazine" OR reddit OR forum OR "neighborhood guide" OR blog',
            preferred_source_kinds=("reddit", "forum", "blog", "local-publication"),
            discouraged_source_kinds=("youtube", "podcast"),
            youtube_results=0,
            podcast_results=0,
        )

    if _looks_like_product_review(lowered):
        return ResearchProfile(
            mode="product_review",
            label="Product Reviews",
            planner_guidance=(
                "Treat this as a product review task. Prioritize hands-on blog posts, owner "
                "reports, Reddit discussions, YouTube reviews, comparative testing, and "
                "reliability or complaint coverage. Avoid retailer pages unless they contain "
                "unique specs that matter."
            ),
            refiner_guidance=(
                "Bias new queries toward blog posts, Reddit threads, owner discussions, "
                "comparisons, complaints, and YouTube reviews. Keep expanding toward durability, "
                "tradeoffs, alternatives, and edge-case ownership feedback."
            ),
            synthesis_guidance=(
                "Answer as a pragmatic buying brief. Make the tradeoffs explicit, highlight who "
                "each option fits, and separate marketing claims from reported real-world use."
            ),
            query_suffix='blog OR reddit OR discussion OR "hands on" OR comparison OR youtube',
            preferred_source_kinds=("blog", "reddit", "youtube", "forum"),
            discouraged_source_kinds=("podcast",),
            youtube_results=6,
            podcast_results=1,
        )

    return ResearchProfile(
        mode="general_research",
        label="General Research",
        planner_guidance=(
            "Treat this as a general research task. Prioritize broad coverage across explainers, "
            "expert analysis, podcasts, interviews, YouTube, and high-signal web sources. Build "
            "lanes that expose competing frameworks, historical context, and current debates."
        ),
        refiner_guidance=(
            "Bias new queries toward podcasts, interviews, explainers, YouTube, and strong web "
            "analysis. Expand into adjacent terms, opposing views, and deeper context rather "
            "than product-style buyer language."
        ),
        synthesis_guidance=(
            "Answer as a research brief. Focus on the clearest conclusions, open questions, "
            "important disagreements, and concrete next steps for deeper study."
        ),
        query_suffix="podcast OR youtube OR interview OR explainer OR analysis OR discussion",
        preferred_source_kinds=("podcast", "youtube", "blog", "forum", "web"),
        discouraged_source_kinds=(),
        youtube_results=4,
        podcast_results=4,
    )


def _matches_any(value: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in value for keyword in keywords)


def _looks_like_product_review(value: str) -> bool:
    if _matches_any(value, PRODUCT_KEYWORDS):
        return True
    if _matches_any(value, GENERAL_RESEARCH_HINTS):
        return False
    return bool(re.search(r"\b[a-z]{3,}\s+(review|reviews|vs|comparison)\b", value))


def resolve_research_profile(
    prompt: str,
    mode: ResearchMode | None = None,
) -> ResearchProfile:
    """Resolve a research profile from an explicit mode or prompt inference."""

    if mode is None:
        return infer_research_profile(prompt)
    return _profile_for_mode(mode)


def parse_research_mode_option(value: ResearchModeOption) -> ResearchMode | None:
    """Convert CLI-facing mode names into internal research modes."""

    mapping: dict[ResearchModeOption, ResearchMode | None] = {
        "auto": None,
        "product": "product_review",
        "restaurant": "restaurant_recommendation",
        "research": "general_research",
    }
    return mapping[value]


def _profile_for_mode(mode: ResearchMode) -> ResearchProfile:
    if mode == "restaurant_recommendation":
        return ResearchProfile(
            mode="restaurant_recommendation",
            label="Restaurant Recommendations",
            planner_guidance=(
                "Treat this as a restaurant recommendation task. Prioritize local magazines, "
                "city guides, neighborhood food publications, Reddit, Chowhound-style forums, "
                "and first-hand diner reports. Avoid generic SEO listicles. YouTube is low-priority "
                "unless the prompt explicitly asks for it."
            ),
            refiner_guidance=(
                "Bias new queries toward local publications, neighborhood discussions, Reddit, "
                "food forums, and menu-specific diner feedback. Avoid generic roundup phrasing "
                "and keep YouTube as a fallback only."
            ),
            synthesis_guidance=(
                "Answer as a recommendation brief. Surface atmosphere, signature dishes, pricing "
                "signals, neighborhood fit, and consensus or disagreement across locals."
            ),
            query_suffix='"local magazine" OR reddit OR forum OR "neighborhood guide" OR blog',
            preferred_source_kinds=("reddit", "forum", "blog", "local-publication"),
            discouraged_source_kinds=("youtube", "podcast"),
            youtube_results=0,
            podcast_results=0,
        )

    if mode == "product_review":
        return ResearchProfile(
            mode="product_review",
            label="Product Reviews",
            planner_guidance=(
                "Treat this as a product review task. Prioritize hands-on blog posts, owner "
                "reports, Reddit discussions, YouTube reviews, comparative testing, and "
                "reliability or complaint coverage. Avoid retailer pages unless they contain "
                "unique specs that matter."
            ),
            refiner_guidance=(
                "Bias new queries toward blog posts, Reddit threads, owner discussions, "
                "comparisons, complaints, and YouTube reviews. Keep expanding toward durability, "
                "tradeoffs, alternatives, and edge-case ownership feedback."
            ),
            synthesis_guidance=(
                "Answer as a pragmatic buying brief. Make the tradeoffs explicit, highlight who "
                "each option fits, and separate marketing claims from reported real-world use."
            ),
            query_suffix='blog OR reddit OR discussion OR "hands on" OR comparison OR youtube',
            preferred_source_kinds=("blog", "reddit", "youtube", "forum"),
            discouraged_source_kinds=("podcast",),
            youtube_results=6,
            podcast_results=1,
        )

    return ResearchProfile(
        mode="general_research",
        label="General Research",
        planner_guidance=(
            "Treat this as a general research task. Prioritize broad coverage across explainers, "
            "expert analysis, podcasts, interviews, YouTube, and high-signal web sources. Build "
            "lanes that expose competing frameworks, historical context, and current debates."
        ),
        refiner_guidance=(
            "Bias new queries toward podcasts, interviews, explainers, YouTube, and strong web "
            "analysis. Expand into adjacent terms, opposing views, and deeper context rather "
            "than product-style buyer language."
        ),
        synthesis_guidance=(
            "Answer as a research brief. Focus on the clearest conclusions, open questions, "
            "important disagreements, and concrete next steps for deeper study."
        ),
        query_suffix="podcast OR youtube OR interview OR explainer OR analysis OR discussion",
        preferred_source_kinds=("podcast", "youtube", "blog", "forum", "web"),
        discouraged_source_kinds=(),
        youtube_results=4,
        podcast_results=4,
    )
