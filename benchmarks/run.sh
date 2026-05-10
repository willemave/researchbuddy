#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BENCH_DIR="$ROOT_DIR/benchmarks"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing Python virtualenv at $PYTHON_BIN" >&2
  exit 1
fi

if [[ -f "$HOME/.cargo/env" ]]; then
  # shellcheck disable=SC1090
  . "$HOME/.cargo/env"
fi

SAMPLE_SIZE="${SAMPLE_SIZE:-100}"
EXTRACT_SAMPLE_SIZE="${EXTRACT_SAMPLE_SIZE:-100}"
PAGE_TIMEOUT_MS="${PAGE_TIMEOUT_MS:-45000}"
RUN_ID="${RUN_ID:-}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="$BENCH_DIR/results/$TIMESTAMP"
LIVE_MANIFEST_PATH="$OUTPUT_DIR/live-corpus.json"
EXTRACT_MANIFEST_PATH="$OUTPUT_DIR/extract-corpus.json"

mkdir -p "$OUTPUT_DIR"

LIVE_CORPUS_ARGS=(
  "$BENCH_DIR/scripts/benchmark_url_corpus.py"
  --output "$LIVE_MANIFEST_PATH"
  --sample-size "$SAMPLE_SIZE"
)

EXTRACT_CORPUS_ARGS=(
  "$BENCH_DIR/scripts/benchmark_url_corpus.py"
  --output "$EXTRACT_MANIFEST_PATH"
  --sample-size "$EXTRACT_SAMPLE_SIZE"
  --require-html
)

if [[ -n "$RUN_ID" ]]; then
  LIVE_CORPUS_ARGS+=(--run-id "$RUN_ID")
  EXTRACT_CORPUS_ARGS+=(--run-id "$RUN_ID")
else
  LIVE_CORPUS_ARGS+=(--all-runs)
  EXTRACT_CORPUS_ARGS+=(--all-runs)
fi

"$PYTHON_BIN" "${LIVE_CORPUS_ARGS[@]}"
"$PYTHON_BIN" "${EXTRACT_CORPUS_ARGS[@]}"

"$PYTHON_BIN" \
  "$BENCH_DIR/scripts/benchmark_crawl4ai.py" \
  --manifest "$LIVE_MANIFEST_PATH" \
  --output "$OUTPUT_DIR/crawl4ai-live.json" \
  --markdown-dir "$OUTPUT_DIR/crawl4ai-live-markdown" \
  --mode live \
  --page-timeout-ms "$PAGE_TIMEOUT_MS"

"$PYTHON_BIN" \
  "$BENCH_DIR/scripts/benchmark_crawl4ai.py" \
  --manifest "$EXTRACT_MANIFEST_PATH" \
  --output "$OUTPUT_DIR/crawl4ai-extract-only.json" \
  --markdown-dir "$OUTPUT_DIR/crawl4ai-extract-only-markdown" \
  --mode extract-only \
  --page-timeout-ms "$PAGE_TIMEOUT_MS"

"$PYTHON_BIN" \
  "$BENCH_DIR/scripts/score_benchmark_quality.py" \
  --manifest "$LIVE_MANIFEST_PATH" \
  --benchmark "$OUTPUT_DIR/crawl4ai-live.json" \
  --output "$OUTPUT_DIR/crawl4ai-live-quality.json"

"$PYTHON_BIN" \
  "$BENCH_DIR/scripts/score_benchmark_quality.py" \
  --manifest "$EXTRACT_MANIFEST_PATH" \
  --benchmark "$OUTPUT_DIR/crawl4ai-extract-only.json" \
  --output "$OUTPUT_DIR/crawl4ai-extract-only-quality.json"

if command -v cargo >/dev/null 2>&1; then
  cargo run --release --manifest-path "$BENCH_DIR/rust-composed-stack/Cargo.toml" -- \
    --manifest "$LIVE_MANIFEST_PATH" \
    --output "$OUTPUT_DIR/rust-static-live.json" \
    --markdown-dir "$OUTPUT_DIR/rust-static-live-markdown" \
    --mode live \
    --tool static \
    --timeout-ms "$PAGE_TIMEOUT_MS"

  cargo run --release --manifest-path "$BENCH_DIR/rust-composed-stack/Cargo.toml" -- \
    --manifest "$LIVE_MANIFEST_PATH" \
    --output "$OUTPUT_DIR/rust-hybrid-live.json" \
    --markdown-dir "$OUTPUT_DIR/rust-hybrid-live-markdown" \
    --mode live \
    --tool hybrid \
    --timeout-ms "$PAGE_TIMEOUT_MS"

  cargo run --release --manifest-path "$BENCH_DIR/rust-composed-stack/Cargo.toml" -- \
    --manifest "$EXTRACT_MANIFEST_PATH" \
    --output "$OUTPUT_DIR/rust-static-extract-only.json" \
    --markdown-dir "$OUTPUT_DIR/rust-static-extract-only-markdown" \
    --mode extract-only \
    --tool static \
    --timeout-ms "$PAGE_TIMEOUT_MS"

  "$PYTHON_BIN" \
    "$BENCH_DIR/scripts/score_benchmark_quality.py" \
    --manifest "$LIVE_MANIFEST_PATH" \
    --benchmark "$OUTPUT_DIR/rust-static-live.json" \
    --output "$OUTPUT_DIR/rust-static-live-quality.json"

  "$PYTHON_BIN" \
    "$BENCH_DIR/scripts/score_benchmark_quality.py" \
    --manifest "$LIVE_MANIFEST_PATH" \
    --benchmark "$OUTPUT_DIR/rust-hybrid-live.json" \
    --output "$OUTPUT_DIR/rust-hybrid-live-quality.json"

  "$PYTHON_BIN" \
    "$BENCH_DIR/scripts/score_benchmark_quality.py" \
    --manifest "$EXTRACT_MANIFEST_PATH" \
    --benchmark "$OUTPUT_DIR/rust-static-extract-only.json" \
    --output "$OUTPUT_DIR/rust-static-extract-only-quality.json"
else
  echo "cargo not found; skipped Rust benchmark harness." >&2
fi

echo "results_dir=$OUTPUT_DIR"
