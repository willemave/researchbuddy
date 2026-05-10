# Benchmarks

This folder contains the crawl-stack benchmark harness and result artifacts for the Rust rewrite investigation.

## Layout

- `scripts/benchmark_url_corpus.py`
  - Builds a mixed corpus from `data/researchbuddy.db`
  - Targets a mix of `youtube`, `podcast`, `js_heavy`, and `general` pages
- `scripts/benchmark_crawl4ai.py`
  - Runs the Python `crawl4ai` benchmark
  - Persists extracted markdown per URL
- `scripts/score_benchmark_quality.py`
  - Scores extracted markdown against the historical saved markdown for the same URL
- `run.sh`
  - End-to-end wrapper for corpus generation, benchmark runs, and quality scoring
- `rust-composed-stack/`
  - Rust harness with:
    - static path: `reqwest` + `dom_smoothie` + `html-to-markdown-rs`
    - hybrid path: browser fallback via `chromiumoxide`
    - YouTube metadata adapter via `rusty_ytdl`
- `results/`
  - Timestamped benchmark outputs

## Current Best Signal

See `report.md` for the latest 100-URL comparison.

The current conclusion is:

1. Rust extraction quality on saved HTML is already strong.
2. Live crawling is the real risk surface.
3. A limited hybrid Rust path is viable.
4. Blanket browser fallback for podcast-heavy domains is too expensive and timeout-prone.
