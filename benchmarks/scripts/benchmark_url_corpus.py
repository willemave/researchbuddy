from __future__ import annotations

import argparse
import json
import math
import sqlite3
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

CATEGORY_ORDER = ("youtube", "podcast", "js_heavy", "general")
CATEGORY_RATIOS = {
    "youtube": 0.12,
    "podcast": 0.38,
    "js_heavy": 0.22,
    "general": 0.28,
}
YOUTUBE_DOMAINS = {
    "www.youtube.com",
    "youtube.com",
    "m.youtube.com",
    "youtu.be",
}
PODCAST_DOMAINS = {
    "podscan.fm",
    "pod.wave.co",
    "podcasts.apple.com",
    "launchpod.logrocket.com",
    "getpodcast.com",
    "open.spotify.com",
    "creators.spotify.com",
    "plinkhq.com",
    "vanishinggradients.fireside.fm",
    "fundbuildscale.podbean.com",
    "www.podcast.de",
    "www.ivoox.com",
    "nzpod.co.nz",
    "podscript.ai",
    "uk-podcasts.co.uk",
    "sfelc.com",
}
JS_HEAVY_DOMAINS = {
    "www.linkedin.com",
    "medium.com",
    "productimpactpod.substack.com",
    "hugobowne.substack.com",
    "open.spotify.com",
    "creators.spotify.com",
    "podcasts.apple.com",
    "www.youtube.com",
    "youtube.com",
}
PODCAST_KEYWORDS = (
    "podcast",
    "podscan",
    "podscript",
    "podbean",
    "fireside",
    "spotify.com/show/",
)
JS_HEAVY_KEYWORDS = (
    "linkedin.com",
    "medium.com",
    "substack.com",
    "youtube.com",
    "spotify.com/show/",
    "podcasts.apple.com",
)


@dataclass(frozen=True)
class CorpusEntry:
    run_id: str
    url: str
    title: str | None
    source_query: str
    domain: str
    category: str
    tags: list[str]
    html_path: str | None
    markdown_path: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a mixed benchmark URL corpus from saved ResearchBuddy runs."
    )
    parser.add_argument(
        "--db-path",
        default="data/researchbuddy.db",
        help="Path to the SQLite database. Default: %(default)s",
    )
    parser.add_argument(
        "--run-id",
        help="Specific run ID to sample from. Defaults to the latest completed run.",
    )
    parser.add_argument(
        "--all-runs",
        action="store_true",
        help="Sample across all fetched URLs in the database instead of a single run.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="Maximum number of URLs to emit. Default: %(default)s",
    )
    parser.add_argument(
        "--require-html",
        action="store_true",
        help="Only include rows with a saved html_path.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON path.",
    )
    return parser.parse_args()


def resolve_run_id(conn: sqlite3.Connection, explicit_run_id: str | None) -> str:
    if explicit_run_id:
        return explicit_run_id

    row = conn.execute(
        """
        SELECT run_id
        FROM runs
        WHERE status = 'completed'
        ORDER BY created_at DESC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        raise RuntimeError("No completed run found in the database.")
    return str(row[0])


def load_entries(
    conn: sqlite3.Connection,
    run_id: str | None,
    *,
    all_runs: bool,
    require_html: bool,
) -> list[CorpusEntry]:
    conditions = ["status = 'fetched'"]
    params: list[object] = []
    if not all_runs:
        conditions.append("run_id = ?")
        if run_id is None:
            raise RuntimeError("run_id is required unless --all-runs is set.")
        params.append(run_id)
    if require_html:
        conditions.append("html_path IS NOT NULL")

    query = f"""
        SELECT run_id, url, title, source_query, html_path, markdown_path
        FROM urls
        WHERE {' AND '.join(conditions)}
        ORDER BY id ASC
    """
    rows = conn.execute(query, params).fetchall()
    entries: list[CorpusEntry] = []
    for row in rows:
        url = str(row[1])
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if not domain:
            continue
        category, tags = classify_entry(url, domain)
        html_path = str(Path(str(row[4])).resolve()) if row[4] else None
        markdown_path = str(Path(str(row[5])).resolve()) if row[5] else None
        entries.append(
            CorpusEntry(
                run_id=str(row[0]),
                url=url,
                title=str(row[2]) if row[2] else None,
                source_query=str(row[3]),
                domain=domain,
                category=category,
                tags=tags,
                html_path=html_path,
                markdown_path=markdown_path,
            )
        )
    return entries


def classify_entry(url: str, domain: str) -> tuple[str, list[str]]:
    lowered = url.lower()
    tags: list[str] = []

    if domain in YOUTUBE_DOMAINS:
        tags.append("youtube")
    if domain in PODCAST_DOMAINS or any(keyword in lowered for keyword in PODCAST_KEYWORDS):
        tags.append("podcast")
    if (
        domain in JS_HEAVY_DOMAINS
        or any(keyword in lowered for keyword in JS_HEAVY_KEYWORDS)
        or "youtube" in tags
    ):
        tags.append("js_heavy")

    for category in CATEGORY_ORDER:
        if category in tags:
            return category, tags
    return "general", tags


def allocate_category_targets(
    entries: list[CorpusEntry],
    sample_size: int,
) -> dict[str, int]:
    available = {
        category: sum(1 for entry in entries if entry.category == category)
        for category in CATEGORY_ORDER
    }
    targets = dict.fromkeys(CATEGORY_ORDER, 0)

    for category in CATEGORY_ORDER:
        desired = math.floor(sample_size * CATEGORY_RATIOS[category])
        targets[category] = min(desired, available[category])

    while sum(targets.values()) < min(sample_size, len(entries)):
        advanced = False
        for category in CATEGORY_ORDER:
            if targets[category] >= available[category]:
                continue
            targets[category] += 1
            advanced = True
            if sum(targets.values()) >= min(sample_size, len(entries)):
                break
        if not advanced:
            break

    return targets


def diversify_by_domain(entries: list[CorpusEntry], sample_size: int) -> list[CorpusEntry]:
    buckets: dict[str, list[CorpusEntry]] = defaultdict(list)
    for entry in entries:
        buckets[entry.domain].append(entry)

    ordered_domains = sorted(buckets, key=lambda domain: (-len(buckets[domain]), domain))
    diversified: list[CorpusEntry] = []
    while ordered_domains and len(diversified) < sample_size:
        next_round: list[str] = []
        for domain in ordered_domains:
            bucket = buckets[domain]
            if bucket:
                diversified.append(bucket.pop(0))
                if len(diversified) >= sample_size:
                    break
            if bucket:
                next_round.append(domain)
        ordered_domains = next_round
    return diversified


def select_mixed_sample(entries: list[CorpusEntry], sample_size: int) -> tuple[list[CorpusEntry], dict[str, int]]:
    selected: list[CorpusEntry] = []
    selected_urls: set[str] = set()
    targets = allocate_category_targets(entries, sample_size)

    for category in CATEGORY_ORDER:
        category_entries = [entry for entry in entries if entry.category == category]
        for entry in diversify_by_domain(category_entries, targets[category]):
            if entry.url in selected_urls:
                continue
            selected.append(entry)
            selected_urls.add(entry.url)

    if len(selected) >= sample_size:
        return selected[:sample_size], targets

    remaining_entries = [entry for entry in entries if entry.url not in selected_urls]
    for entry in diversify_by_domain(remaining_entries, sample_size - len(selected)):
        selected.append(entry)
        selected_urls.add(entry.url)
        if len(selected) >= sample_size:
            break

    return selected, targets


def count_by_category(entries: list[CorpusEntry]) -> dict[str, int]:
    counts = dict.fromkeys(CATEGORY_ORDER, 0)
    for entry in entries:
        counts[entry.category] += 1
    return counts


def count_by_tag(entries: list[CorpusEntry]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for entry in entries:
        for tag in entry.tags:
            counts[tag] += 1
    return dict(sorted(counts.items()))


def main() -> None:
    args = parse_args()
    db_path = Path(args.db_path)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        run_id = None if args.all_runs else resolve_run_id(conn, args.run_id)
        entries = load_entries(
            conn,
            run_id,
            all_runs=args.all_runs,
            require_html=args.require_html,
        )

    selected, targets = select_mixed_sample(entries, args.sample_size)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "db_path": str(db_path.resolve()),
        "run_id": run_id,
        "all_runs": bool(args.all_runs),
        "require_html": bool(args.require_html),
        "total_fetched_urls": len(entries),
        "available_by_category": count_by_category(entries),
        "available_by_tag": count_by_tag(entries),
        "sample_targets": targets,
        "selected_by_category": count_by_category(selected),
        "selected_by_tag": count_by_tag(selected),
        "sample_size": len(selected),
        "entries": [asdict(entry) for entry in selected],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.all_runs:
        print("run_scope=all-runs")
    else:
        print(f"run_id={run_id}")
    print(f"total_fetched_urls={len(entries)}")
    print(f"sample_size={len(selected)}")
    print(f"available_by_category={json.dumps(payload['available_by_category'], sort_keys=True)}")
    print(f"selected_by_category={json.dumps(payload['selected_by_category'], sort_keys=True)}")
    print(f"output={output_path}")


if __name__ == "__main__":
    main()
