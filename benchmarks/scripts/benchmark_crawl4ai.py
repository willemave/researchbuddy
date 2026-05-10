from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import platform
import statistics
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)

DEFAULT_EXCLUDED_TAGS = ["script", "style", "noscript", "nav", "footer", "aside", "form"]


@dataclass(frozen=True)
class BenchResult:
    url: str
    domain: str
    category: str
    tags: list[str]
    mode: str
    strategy: str
    success: bool
    elapsed_ms: float
    markdown_chars: int
    markdown_output_path: str | None = None
    error: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark Crawl4AI on a saved ResearchBuddy URL corpus."
    )
    parser.add_argument("--manifest", required=True, help="Corpus manifest JSON file.")
    parser.add_argument("--output", required=True, help="Output JSON file.")
    parser.add_argument(
        "--mode",
        choices=("live", "extract-only"),
        required=True,
        help="Benchmark fresh crawling or extraction from saved HTML.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit after reading manifest entries. Default: all entries.",
    )
    parser.add_argument(
        "--page-timeout-ms",
        type=int,
        default=45_000,
        help="Crawl4AI page timeout. Default: %(default)s",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use headless browser mode. Default: %(default)s",
    )
    parser.add_argument(
        "--markdown-dir",
        help="Optional directory for extracted markdown artifacts.",
    )
    return parser.parse_args()


def select_markdown_text(markdown_result: Any) -> str:
    fit_markdown = (getattr(markdown_result, "fit_markdown", "") or "").strip()
    if fit_markdown:
        return fit_markdown

    markdown_with_citations = (
        getattr(markdown_result, "markdown_with_citations", "") or ""
    ).strip()
    if markdown_with_citations:
        return markdown_with_citations

    return (getattr(markdown_result, "raw_markdown", "") or "").strip()


def build_run_config(page_timeout_ms: int) -> CrawlerRunConfig:
    return CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        verbose=False,
        log_console=False,
        wait_until="domcontentloaded",
        page_timeout=page_timeout_ms,
        remove_forms=True,
        excluded_tags=DEFAULT_EXCLUDED_TAGS,
        word_count_threshold=1,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.48),
            content_source="cleaned_html",
        ),
    )


def load_manifest(manifest_path: Path, limit: int) -> dict[str, Any]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = payload.get("entries", [])
    if limit > 0:
        entries = entries[:limit]
    payload["entries"] = entries
    return payload


def summarize(results: list[BenchResult]) -> dict[str, Any]:
    elapsed = [result.elapsed_ms for result in results if result.success]
    markdown_chars = [result.markdown_chars for result in results if result.success]
    summary = {
        "total": len(results),
        "successes": sum(1 for result in results if result.success),
        "failures": sum(1 for result in results if not result.success),
    }
    if not elapsed:
        return summary
    ordered = sorted(elapsed)
    summary.update(
        {
            "mean_elapsed_ms": statistics.fmean(elapsed),
            "median_elapsed_ms": statistics.median(elapsed),
            "p95_elapsed_ms": percentile(ordered, 95),
            "min_elapsed_ms": ordered[0],
            "max_elapsed_ms": ordered[-1],
            "mean_markdown_chars": statistics.fmean(markdown_chars) if markdown_chars else 0.0,
        }
    )
    return summary


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    rank = (len(values) - 1) * (p / 100)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return values[lower]
    weight = rank - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def write_markdown(markdown_dir: Path | None, url: str, markdown: str) -> str | None:
    if markdown_dir is None:
        return None
    markdown_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    output_path = markdown_dir / f"{digest}.md"
    output_path.write_text(markdown, encoding="utf-8")
    return str(output_path.resolve())


async def benchmark_live(
    entries: list[dict[str, Any]],
    page_timeout_ms: int,
    headless: bool,
    markdown_dir: Path | None,
) -> list[BenchResult]:
    browser_config = BrowserConfig(headless=headless, verbose=False)
    run_config = build_run_config(page_timeout_ms)
    results: list[BenchResult] = []
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for entry in entries:
            url = entry["url"]
            start = perf_counter()
            try:
                result = await crawler.arun(url=url, config=run_config)
                elapsed_ms = (perf_counter() - start) * 1000
                if not getattr(result, "success", False):
                    error = getattr(result, "error_message", None) or getattr(
                        result, "error", "unknown error"
                    )
                    results.append(
                        BenchResult(
                            url=url,
                            domain=entry["domain"],
                            category=entry["category"],
                            tags=entry.get("tags", []),
                            mode="live",
                            strategy="crawl4ai-browser",
                            success=False,
                            elapsed_ms=elapsed_ms,
                            markdown_chars=0,
                            error=str(error),
                        )
                    )
                    continue
                markdown = select_markdown_text(getattr(result, "markdown", None))
                markdown_output_path = write_markdown(markdown_dir, url, markdown)
                results.append(
                    BenchResult(
                        url=url,
                        domain=entry["domain"],
                        category=entry["category"],
                        tags=entry.get("tags", []),
                        mode="live",
                        strategy="crawl4ai-browser",
                        success=True,
                        elapsed_ms=elapsed_ms,
                        markdown_chars=len(markdown),
                        markdown_output_path=markdown_output_path,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    BenchResult(
                        url=url,
                        domain=entry["domain"],
                        category=entry["category"],
                        tags=entry.get("tags", []),
                        mode="live",
                        strategy="crawl4ai-browser",
                        success=False,
                        elapsed_ms=(perf_counter() - start) * 1000,
                        markdown_chars=0,
                        error=str(exc),
                    )
                )
    return results


async def benchmark_extract_only(
    entries: list[dict[str, Any]],
    page_timeout_ms: int,
    headless: bool,
    markdown_dir: Path | None,
) -> list[BenchResult]:
    browser_config = BrowserConfig(headless=headless, verbose=False)
    run_config = build_run_config(page_timeout_ms)
    results: list[BenchResult] = []
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for entry in entries:
            url = entry["url"]
            html_path = entry.get("html_path")
            start = perf_counter()
            if not html_path:
                results.append(
                    BenchResult(
                        url=url,
                        domain=entry["domain"],
                        category=entry["category"],
                        tags=entry.get("tags", []),
                        mode="extract-only",
                        strategy="crawl4ai-browser",
                        success=False,
                        elapsed_ms=(perf_counter() - start) * 1000,
                        markdown_chars=0,
                        error="html_path missing from manifest entry",
                    )
                )
                continue
            try:
                file_url = Path(html_path).resolve().as_uri()
                result = await crawler.arun(url=file_url, config=run_config)
                elapsed_ms = (perf_counter() - start) * 1000
                if not getattr(result, "success", False):
                    error = getattr(result, "error_message", None) or getattr(
                        result, "error", "unknown error"
                    )
                    results.append(
                        BenchResult(
                            url=url,
                            domain=entry["domain"],
                            category=entry["category"],
                            tags=entry.get("tags", []),
                            mode="extract-only",
                            strategy="crawl4ai-browser",
                            success=False,
                            elapsed_ms=elapsed_ms,
                            markdown_chars=0,
                            error=str(error),
                        )
                    )
                    continue
                markdown = select_markdown_text(getattr(result, "markdown", None))
                markdown_output_path = write_markdown(markdown_dir, url, markdown)
                results.append(
                    BenchResult(
                        url=url,
                        domain=entry["domain"],
                        category=entry["category"],
                        tags=entry.get("tags", []),
                        mode="extract-only",
                        strategy="crawl4ai-browser",
                        success=True,
                        elapsed_ms=elapsed_ms,
                        markdown_chars=len(markdown),
                        markdown_output_path=markdown_output_path,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    BenchResult(
                        url=url,
                        domain=entry["domain"],
                        category=entry["category"],
                        tags=entry.get("tags", []),
                        mode="extract-only",
                        strategy="crawl4ai-browser",
                        success=False,
                        elapsed_ms=(perf_counter() - start) * 1000,
                        markdown_chars=0,
                        error=str(exc),
                    )
                )
    return results


async def async_main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    output_path = Path(args.output)
    markdown_dir = Path(args.markdown_dir) if args.markdown_dir else None
    output_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(manifest_path, args.limit)
    entries = manifest["entries"]
    if args.mode == "live":
        results = await benchmark_live(entries, args.page_timeout_ms, args.headless, markdown_dir)
    else:
        results = await benchmark_extract_only(
            entries,
            args.page_timeout_ms,
            args.headless,
            markdown_dir,
        )

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "tool": "crawl4ai",
        "mode": args.mode,
        "manifest": str(manifest_path.resolve()),
        "limit": args.limit,
        "page_timeout_ms": args.page_timeout_ms,
        "headless": args.headless,
        "markdown_dir": str(markdown_dir.resolve()) if markdown_dir else None,
        "platform": {
            "python": platform.python_version(),
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "summary": summarize(results),
        "results": [asdict(result) for result in results],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    summary = payload["summary"]
    print(f"tool=crawl4ai mode={args.mode}")
    print(f"total={summary['total']} successes={summary['successes']} failures={summary['failures']}")
    if summary["successes"] > 0:
        print(
            "mean_elapsed_ms="
            f"{summary['mean_elapsed_ms']:.2f} median_elapsed_ms={summary['median_elapsed_ms']:.2f} "
            f"p95_elapsed_ms={summary['p95_elapsed_ms']:.2f}"
        )
    print(f"output={output_path}")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
