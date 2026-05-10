from __future__ import annotations

import argparse
import difflib
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]{1,}")


@dataclass(frozen=True)
class QualityResult:
    url: str
    domain: str
    category: str
    tags: list[str]
    strategy: str
    success: bool
    overall_score: float
    token_f1: float
    sequence_ratio: float
    heading_recall: float
    length_score: float
    reference_chars: int
    output_chars: int
    markdown_output_path: str | None
    reference_markdown_path: str | None
    error: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score benchmark markdown quality against historical markdown artifacts."
    )
    parser.add_argument("--manifest", required=True, help="Corpus manifest JSON file.")
    parser.add_argument("--benchmark", required=True, help="Benchmark JSON file.")
    parser.add_argument("--output", required=True, help="Output JSON file.")
    return parser.parse_args()


def normalize_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip().lower()


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def extract_headings(text: str) -> set[str]:
    headings = set()
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip().lower()
        if line.lstrip().startswith("#") and stripped:
            headings.add(stripped)
    return headings


def clipped_sequence_ratio(reference: str, output: str) -> float:
    return difflib.SequenceMatcher(
        a=reference[:20_000],
        b=output[:20_000],
        autojunk=False,
    ).ratio()


def token_f1(reference_tokens: list[str], output_tokens: list[str]) -> float:
    if not reference_tokens or not output_tokens:
        return 0.0

    reference_counts = Counter(reference_tokens)
    output_counts = Counter(output_tokens)
    overlap = sum(min(reference_counts[token], output_counts[token]) for token in output_counts)
    if overlap == 0:
        return 0.0

    precision = overlap / max(1, len(output_tokens))
    recall = overlap / max(1, len(reference_tokens))
    return 2 * precision * recall / max(1e-9, precision + recall)


def heading_recall(reference_headings: set[str], output_headings: set[str]) -> float:
    if not reference_headings:
        return 1.0 if not output_headings else 0.8
    if not output_headings:
        return 0.0
    matched = len(reference_headings & output_headings)
    return matched / len(reference_headings)


def length_score(reference_chars: int, output_chars: int) -> float:
    if reference_chars == 0 or output_chars == 0:
        return 0.0
    ratio = output_chars / reference_chars
    return math.exp(-abs(math.log(ratio)))


def overall_score(
    token_f1_score: float,
    sequence_ratio_score: float,
    heading_recall_score: float,
    length_score_value: float,
) -> float:
    return (
        token_f1_score * 0.45
        + sequence_ratio_score * 0.25
        + heading_recall_score * 0.15
        + length_score_value * 0.15
    )


def summarize_scores(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    ordered = sorted(values)
    return {
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "min": ordered[0],
        "max": ordered[-1],
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_manifest_map(manifest: dict) -> dict[str, dict]:
    return {entry["url"]: entry for entry in manifest["entries"]}


def read_text(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def score_result(result: dict, manifest_entry: dict | None) -> QualityResult:
    if manifest_entry is None:
        return QualityResult(
            url=result["url"],
            domain=result.get("domain", ""),
            category=result.get("category", "general"),
            tags=result.get("tags", []),
            strategy=result.get("strategy", "unknown"),
            success=False,
            overall_score=0.0,
            token_f1=0.0,
            sequence_ratio=0.0,
            heading_recall=0.0,
            length_score=0.0,
            reference_chars=0,
            output_chars=0,
            markdown_output_path=result.get("markdown_output_path"),
            reference_markdown_path=None,
            error="manifest entry missing for benchmark result",
        )

    reference_path = manifest_entry.get("markdown_path")
    output_path = result.get("markdown_output_path")
    reference = normalize_markdown(read_text(reference_path))
    output = normalize_markdown(read_text(output_path))
    if not result.get("success") or not output:
        return QualityResult(
            url=result["url"],
            domain=manifest_entry["domain"],
            category=manifest_entry["category"],
            tags=manifest_entry.get("tags", []),
            strategy=result.get("strategy", "unknown"),
            success=bool(result.get("success", False)),
            overall_score=0.0,
            token_f1=0.0,
            sequence_ratio=0.0,
            heading_recall=0.0,
            length_score=0.0,
            reference_chars=len(reference),
            output_chars=len(output),
            markdown_output_path=output_path,
            reference_markdown_path=reference_path,
            error=result.get("error"),
        )

    score_token_f1 = token_f1(tokenize(reference), tokenize(output))
    score_sequence_ratio = clipped_sequence_ratio(reference, output)
    score_heading_recall = heading_recall(extract_headings(reference), extract_headings(output))
    score_length = length_score(len(reference), len(output))

    return QualityResult(
        url=result["url"],
        domain=manifest_entry["domain"],
        category=manifest_entry["category"],
        tags=manifest_entry.get("tags", []),
        strategy=result.get("strategy", "unknown"),
        success=True,
        overall_score=overall_score(
            score_token_f1,
            score_sequence_ratio,
            score_heading_recall,
            score_length,
        ),
        token_f1=score_token_f1,
        sequence_ratio=score_sequence_ratio,
        heading_recall=score_heading_recall,
        length_score=score_length,
        reference_chars=len(reference),
        output_chars=len(output),
        markdown_output_path=output_path,
        reference_markdown_path=reference_path,
    )


def summarize_results(results: list[QualityResult]) -> dict:
    overall_scores = [result.overall_score for result in results]
    by_category: dict[str, list[float]] = defaultdict(list)
    by_tag: dict[str, list[float]] = defaultdict(list)
    by_domain: dict[str, list[float]] = defaultdict(list)
    for result in results:
        by_category[result.category].append(result.overall_score)
        by_domain[result.domain].append(result.overall_score)
        for tag in result.tags:
            by_tag[tag].append(result.overall_score)

    return {
        "total": len(results),
        "successes": sum(1 for result in results if result.success),
        "failures": sum(1 for result in results if not result.success),
        "overall_score": summarize_scores(overall_scores),
        "metric_means": {
            "token_f1": statistics.fmean(result.token_f1 for result in results),
            "sequence_ratio": statistics.fmean(result.sequence_ratio for result in results),
            "heading_recall": statistics.fmean(result.heading_recall for result in results),
            "length_score": statistics.fmean(result.length_score for result in results),
        },
        "by_category": {
            key: summarize_scores(values) for key, values in sorted(by_category.items())
        },
        "by_tag": {key: summarize_scores(values) for key, values in sorted(by_tag.items())},
        "by_domain": {
            key: summarize_scores(values)
            for key, values in sorted(
                by_domain.items(),
                key=lambda item: (-len(item[1]), item[0]),
            )
        },
    }


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    benchmark_path = Path(args.benchmark)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = load_json(manifest_path)
    benchmark = load_json(benchmark_path)
    manifest_map = build_manifest_map(manifest)
    results = [score_result(result, manifest_map.get(result["url"])) for result in benchmark["results"]]

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "manifest": str(manifest_path.resolve()),
        "benchmark": str(benchmark_path.resolve()),
        "tool": benchmark.get("tool"),
        "mode": benchmark.get("mode"),
        "summary": summarize_results(results),
        "results": [asdict(result) for result in results],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    overall = payload["summary"]["overall_score"]
    print(
        "quality_score_mean="
        f"{overall['mean']:.4f} median={overall['median']:.4f} "
        f"min={overall['min']:.4f} max={overall['max']:.4f}"
    )
    print(f"output={output_path}")


if __name__ == "__main__":
    main()
