from app.agents.lane_planner import LANE_PLANNER_SYSTEM_PROMPT
from app.agents.lane_refiner import LANE_REFINER_SYSTEM_PROMPT
from app.agents.synthesizer import FINAL_SYNTHESIZER_SYSTEM_PROMPT
from app.services.research_profiles import infer_research_profile


def test_lane_planner_prompt_is_generic() -> None:
    assert "research lanes" in LANE_PLANNER_SYSTEM_PROMPT
    assert "source diversity" in LANE_PLANNER_SYSTEM_PROMPT
    assert "Prefer natural-language queries" in LANE_PLANNER_SYSTEM_PROMPT


def test_lane_refiner_prompt_is_generic() -> None:
    assert "evidence gaps" in LANE_REFINER_SYSTEM_PROMPT
    assert "brittle site: filters" in LANE_REFINER_SYSTEM_PROMPT
    assert "do not repeat existing queries" in LANE_REFINER_SYSTEM_PROMPT


def test_final_synthesizer_prompt_is_generic() -> None:
    assert "grounded research" in FINAL_SYNTHESIZER_SYSTEM_PROMPT
    assert "clear about uncertainty" in FINAL_SYNTHESIZER_SYSTEM_PROMPT


def test_infer_research_profile_for_product_review() -> None:
    profile = infer_research_profile("best espresso grinder review")

    assert profile.mode == "product_review"
    assert profile.youtube_results > 0
    assert "youtube" in profile.query_suffix


def test_infer_research_profile_for_restaurants() -> None:
    profile = infer_research_profile("best sushi restaurants in san francisco")

    assert profile.mode == "restaurant_recommendation"
    assert profile.youtube_results == 0
    assert "local magazines" in profile.planner_guidance


def test_infer_research_profile_for_general_research() -> None:
    profile = infer_research_profile(
        "research the history and current debate around nuclear fusion"
    )

    assert profile.mode == "general_research"
    assert profile.podcast_results > 0
    assert "podcasts" in profile.refiner_guidance
