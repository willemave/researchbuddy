# Crawl Benchmark Report

## Run

Timestamp: `20260409-191015`

Artifacts live under:

- `benchmarks/results/20260409-191015/`

Corpus mix:

- total live URLs: `100`
- `youtube`: `11`
- `podcast`: `46`
- `js_heavy`: `16`
- `general`: `27`

## Stacks Compared

### Crawl4AI

- Browser-driven crawl via Playwright
- Existing Python baseline

### Rust Static

- `reqwest`
- `dom_smoothie`
- `html-to-markdown-rs`
- `rusty_ytdl` for YouTube metadata

### Rust Hybrid

- Same static stack
- `chromiumoxide` browser fallback
- Browser fallback for JS-heavy pages and thin/failed static output

## Live Results

| Stack | Success | Mean | Median | P95 | Mean Quality |
|---|---:|---:|---:|---:|---:|
| Crawl4AI | 99/100 | 1498.47 ms | 1105.83 ms | 3281.57 ms | 0.6876 |
| Rust Static | 95/100 | 626.67 ms | 422.92 ms | 1536.93 ms | 0.5497 |
| Rust Hybrid | 100/100 | 2420.06 ms | 890.45 ms | 4049.46 ms | 0.5811 |

Quality scores are benchmark-relative heuristics against the historical saved markdown for the same URL. They are useful for comparison within this repo, not as an absolute external standard.

## Extract-only Results

Saved HTML existed for 11 historical YouTube pages.

| Stack | Success | Mean | Mean Quality |
|---|---:|---:|---:|
| Crawl4AI | 11/11 | 1.34 ms | 0.9989 |
| Rust Static | 11/11 | 0.22 ms | 0.9932 |

## Category Highlights

### Crawl4AI live quality

- `general`: `0.7962`
- `js_heavy`: `0.7163`
- `podcast`: `0.7261`
- `youtube`: `0.2184`

### Rust Static live quality

- `general`: `0.6605`
- `js_heavy`: `0.6380`
- `podcast`: `0.4816`
- `youtube`: `0.4343`

### Rust Hybrid live quality

- `general`: `0.6594`
- `js_heavy`: `0.6376`
- `podcast`: `0.5506`
- `youtube`: `0.4343`

## What Improved

1. The YouTube path is no longer a hard failure in Rust.
2. The limited Rust hybrid path reached `100/100` success on the live corpus.
3. Podcast quality improved from `0.4816` to `0.5506` with browser fallback.

## What Did Not Improve Enough

1. Rust hybrid still trails Crawl4AI on aggregate live quality: `0.5811` vs `0.6876`.
2. The current browser fallback barely changes `general` and `js_heavy` quality.
3. Several podcast domains remain poor even with fallback or metadata rescue:
   - `pod.wave.co`
   - `uk-podcasts.co.uk`
   - `www.podcast.de`
   - `metacast.app`
   - `www.it-labs.com`

## Strategy Distribution For Rust Hybrid

- `static-readability`: `82`
- `youtube-rusty_ytdl`: `11`
- `browser-readability`: `5`
- `browser-metadata`: `1`
- `static-metadata`: `1`

This explains the modest quality gain. The current hybrid policy is still mostly static.

## Rejected Variant

I tested a more aggressive policy that forced browser fallback for podcast pages by default.

That variant was stopped before completion because it became timeout-heavy and progressed too slowly to be practical. The operational result matters:

- blanket browser fallback for the podcast-heavy slice is not the right Rust policy
- the next step should be domain-specific adapters, not simply "more browser"

## Conclusion

The benchmark supports a hybrid Rust rewrite, but not a pure static extractor and not a blanket browser strategy.

The best current Rust shape is:

1. Static fetch and extraction by default
2. Browser fallback only for a targeted subset
3. Domain-specific adapters where the browser still does not produce good markdown

The clearest adapter targets from this run are:

1. podcast aggregators and podcast episode hosts
2. Apple/Spotify-style directory pages
3. YouTube, which already improved with a dedicated adapter
