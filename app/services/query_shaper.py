"""Query shaping helpers to bias toward non-ecommerce sources."""

import re

from pydantic import BaseModel, Field


class QueryShapeRequest(BaseModel):
    """Request payload for shaping a query."""

    query: str
    suffix: str = Field(default="")
    enabled: bool = True


class QueryShapeResult(BaseModel):
    """Result of shaping a query."""

    query: str
    applied: bool


def shape_query(request: QueryShapeRequest) -> QueryShapeResult:
    """Shape a query to bias toward forums, blogs, and discussions.

    Args:
        request: Query shaping request.

    Returns:
        QueryShapeResult with the shaped query and applied flag.
    """

    if not request.enabled or not request.suffix:
        return QueryShapeResult(query=request.query, applied=False)

    filtered_suffix = _filter_suffix(request.query, request.suffix)
    if not filtered_suffix:
        return QueryShapeResult(query=request.query, applied=False)

    shaped = f"{request.query} {filtered_suffix}".strip()
    return QueryShapeResult(query=shaped, applied=shaped != request.query)


def _filter_suffix(query: str, suffix: str) -> str:
    lowered_query = query.lower()
    clauses = [clause.strip() for clause in re.split(r"\s+OR\s+", suffix) if clause.strip()]
    remaining = [
        clause
        for clause in clauses
        if not _query_contains_clause(lowered_query, _normalize_clause(clause))
    ]
    return " OR ".join(remaining)


def _normalize_clause(value: str) -> str:
    return value.strip().strip('"').strip("'").lower()


def _query_contains_clause(lowered_query: str, clause: str) -> bool:
    if " " in clause:
        return clause in lowered_query
    return re.search(rf"\b{re.escape(clause)}\b", lowered_query) is not None
