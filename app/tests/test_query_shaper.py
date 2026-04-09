from app.services.query_shaper import QueryShapeRequest, shape_query


def test_shape_query_applies_suffix() -> None:
    request = QueryShapeRequest(query="best dishwasher", suffix="forum")
    result = shape_query(request)
    assert result.applied is True
    assert result.query.endswith("forum")


def test_shape_query_skips_when_keyword_present() -> None:
    request = QueryShapeRequest(query="best dishwasher forum", suffix="forum")
    result = shape_query(request)
    assert result.applied is False
    assert result.query == request.query


def test_shape_query_disabled() -> None:
    request = QueryShapeRequest(query="best dishwasher", suffix="forum", enabled=False)
    result = shape_query(request)
    assert result.applied is False
    assert result.query == request.query


def test_shape_query_appends_only_missing_suffix_clauses() -> None:
    request = QueryShapeRequest(
        query="AI org design podcast",
        suffix="podcast OR youtube OR interview",
    )
    result = shape_query(request)
    assert result.applied is True
    assert result.query == "AI org design podcast youtube OR interview"


def test_shape_query_uses_word_boundaries_for_single_terms() -> None:
    request = QueryShapeRequest(
        query="analytical methods for AI org design",
        suffix="analysis OR interview",
    )
    result = shape_query(request)
    assert result.applied is True
    assert result.query == "analytical methods for AI org design analysis OR interview"
