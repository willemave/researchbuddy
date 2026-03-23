from app.agents.lane_planner import LANE_PLANNER_SYSTEM_PROMPT
from app.agents.lane_refiner import LANE_REFINER_SYSTEM_PROMPT


def test_lane_planner_prompt_biases_service_provider_reviews() -> None:
    assert "service providers" in LANE_PLANNER_SYSTEM_PROMPT
    assert "Reddit" in LANE_PLANNER_SYSTEM_PROMPT
    assert "Yelp" in LANE_PLANNER_SYSTEM_PROMPT
    assert "customer reviews" in LANE_PLANNER_SYSTEM_PROMPT


def test_lane_refiner_prompt_biases_service_provider_reviews() -> None:
    assert "service providers" in LANE_REFINER_SYSTEM_PROMPT
    assert "Reddit" in LANE_REFINER_SYSTEM_PROMPT
    assert "Yelp" in LANE_REFINER_SYSTEM_PROMPT
    assert "customer-feedback sources" in LANE_REFINER_SYSTEM_PROMPT
