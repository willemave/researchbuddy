from pathlib import Path

import pytest

from app.models.review import UrlTask
from app.services.research_profiles import infer_research_profile
from app.services.url_handlers import fetch_custom_content
from app.workflows import review


class _Reporter:
    def __init__(self) -> None:
        self.results: list[bool] = []

    def on_url_done(self, success: bool) -> None:
        self.results.append(success)


class _ContextThatMustNotCrawl:
    async def new_page(self) -> None:
        raise AssertionError("provider content should bypass Playwright crawling")


@pytest.mark.asyncio
async def test_crawl_single_uses_provider_content_before_playwright(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    task = UrlTask(
        url="https://example.com/provider",
        title="Provider Result",
        source_query="best quiet dishwasher",
        lane_name="Community Reviews",
        provider_name="exa",
        provider_markdown="# Provider markdown",
    )
    stored: dict[str, str] = {}

    async def fake_fetch_custom_content(
        url: str,
        run_paths: dict[str, Path],
    ) -> None:
        return None

    async def fake_store_provider_fetched(
        run_id: str,
        task_arg: UrlTask,
        run_paths: dict[str, Path],
    ) -> None:
        stored["run_id"] = run_id
        stored["markdown"] = task_arg.provider_markdown or ""

    monkeypatch.setattr(review, "_maybe_fetch_custom_content", fake_fetch_custom_content)
    monkeypatch.setattr(review, "_store_provider_fetched", fake_store_provider_fetched)

    reporter = _Reporter()
    run_paths = {
        "html": tmp_path / "html",
        "markdown": tmp_path / "markdown",
        "videos": tmp_path / "videos",
        "transcripts": tmp_path / "transcripts",
        "pdf": tmp_path / "pdf",
    }

    await review._crawl_single(
        run_id="run-123",
        task=task,
        context=_ContextThatMustNotCrawl(),
        headful_fallback={},
        run_paths=run_paths,
        timeout_ms=1000,
        usage_tracker=None,
        reporter=reporter,
    )

    assert stored == {
        "run_id": "run-123",
        "markdown": "# Provider markdown",
    }
    assert reporter.results == [True]


@pytest.mark.asyncio
async def test_collect_youtube_transcripts_returns_empty_on_timeout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def fake_ingest(*args, **kwargs):  # noqa: ANN002, ANN003
        raise TimeoutError("timed out")

    monkeypatch.setattr(review, "transcribe_youtube_videos_with_timeout", fake_ingest)

    transcripts = await review._collect_youtube_transcripts(
        prompt="quiet dishwasher",
        videos_dir=tmp_path / "videos",
        transcripts_dir=tmp_path / "transcripts",
        max_videos=2,
        model_name="base",
        research_profile=infer_research_profile("quiet dishwasher"),
        usage_tracker=None,
    )

    assert transcripts == []


@pytest.mark.asyncio
async def test_collect_podcast_transcripts_returns_empty_on_timeout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    async def fake_search(*args, **kwargs):  # noqa: ANN002, ANN003
        return []

    monkeypatch.setattr(review, "_search_podcast_episodes", fake_search)

    transcripts = await review._collect_podcast_transcripts(
        prompt="history of fusion energy",
        audio_dir=tmp_path / "audio",
        transcripts_dir=tmp_path / "transcripts",
        max_episodes=2,
        model_name="base",
        research_profile=infer_research_profile("history of fusion energy"),
        usage_tracker=None,
    )

    assert transcripts == []


def test_fetch_custom_content_does_not_route_podcast_pages(tmp_path: Path) -> None:
    result = fetch_custom_content(
        "https://podcasts.apple.com/us/podcast/show/id123?i=1000744678894",
        tmp_path / "videos",
        tmp_path / "transcripts",
        tmp_path / "pdf",
    )

    assert result is None
