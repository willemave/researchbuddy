from app.services import semantic_dedupe


def test_cluster_texts_by_similarity_keeps_distinct_source_type_terms(monkeypatch) -> None:
    monkeypatch.setattr(
        semantic_dedupe,
        "embed_texts",
        lambda texts, task_description: [
            (1.0, 0.0),
            (1.0, 0.0),
            (0.0, 1.0),
        ],
    )

    clusters = semantic_dedupe.cluster_texts_by_similarity(
        [
            "best quiet dishwasher reddit",
            "best quiet dishwasher youtube",
            "dishwasher reliability complaints",
        ],
        task_description=semantic_dedupe.QUERY_EMBEDDING_TASK,
        similarity_threshold=0.9,
    )

    assert clusters == [[0], [1], [2]]


def test_dedupe_items_by_text_removes_semantic_duplicates(monkeypatch) -> None:
    monkeypatch.setattr(
        semantic_dedupe,
        "cluster_texts_by_similarity",
        lambda texts, task_description, similarity_threshold: [[0, 1], [2]],
    )

    deduped = semantic_dedupe.dedupe_items_by_text(
        [
            "quiet dishwasher owner reviews",
            "quiet dishwasher user reviews",
            "dishwasher reliability complaints",
        ],
        text_getter=lambda value: value,
        task_description=semantic_dedupe.QUERY_EMBEDDING_TASK,
        similarity_threshold=0.9,
        utility_scorer=len,
    )

    assert deduped == [
        "quiet dishwasher owner reviews",
        "dishwasher reliability complaints",
    ]


def test_mmr_rank_texts_prefers_novel_item_second(monkeypatch) -> None:
    monkeypatch.setattr(
        semantic_dedupe,
        "embed_texts",
        lambda texts, task_description: [
            (1.0, 0.0, 0.0),
            (0.95, 0.05, 0.0),
            (0.0, 1.0, 0.0),
        ],
    )

    ordered = semantic_dedupe.mmr_rank_texts(
        ["card a", "card b", "card c"],
        [0.95, 0.9, 0.75],
        task_description=semantic_dedupe.SOURCE_CARD_EMBEDDING_TASK,
        lambda_mult=0.7,
    )

    assert ordered == [0, 2, 1]
