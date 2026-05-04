# ResearchBuddy Architecture

ResearchBuddy is a packaged CLI, not a hosted web app. A run starts from a user
prompt, plans independent research lanes, gathers source material, compresses
that material into evidence cards, and synthesizes a cited markdown answer.

## Runtime Shape

```text
CLI command
  -> app/cli.py
  -> app/workflows/review.py
  -> lane planning and refinement agents
  -> search providers and local ingestion
  -> evidence cards and lane summaries
  -> hierarchical merge synthesis
  -> saved run bundle and follow-up memory
```

The CLI is built with Typer and distributed as the `researchbuddy` command. The
core workflow is asynchronous so lanes can search, crawl, and process sources in
parallel while still writing deterministic run artifacts.

## Main Modules

| Path | Responsibility |
|------|----------------|
| `app/cli.py` | Command parsing, user-facing output, result-file handling, and command groups |
| `app/workflows/review.py` | End-to-end run orchestration, lane execution, evidence ranking, and synthesis flow |
| `app/agents/` | Prompt builders and local-agent calls for planning, refinement, and synthesis |
| `app/services/search_provider.py` | Exa, Tavily, and Firecrawl search-provider adapters |
| `app/services/playwright_fetcher.py` | Browser capture and headful fallback for difficult pages |
| `app/services/url_handlers.py` | Custom handling for PDFs, Reddit, YouTube, podcasts, and direct content |
| `app/services/storage.py` | SQLite run records, URL status records, and artifact paths |
| `app/services/codex_exec.py` | Local agent harness abstraction for Codex, Claude, and Amp |
| `app/services/homebrew_tap.py` | Homebrew tap formula, docs, workflow, and maintainer skill rendering |
| `app/core/settings.py` | Pydantic settings and provider-key discovery from local agent configs |

## Research Flow

1. `researchbuddy run "<prompt>"` builds a `ReviewRunRequest`.
2. The workflow initializes SQLite state and a run directory under
   `data/storage/<run_id>/`.
3. The research profile resolver selects product, restaurant, or general
   research behavior.
4. The lane planner creates independent lanes with seed queries.
5. Each lane searches providers, deduplicates URLs, crawls pages, handles
   supported rich sources, and refines follow-up queries from early evidence.
6. Captured HTML, converted markdown, transcript metadata, and URL statuses are
   written into the run bundle.
7. Source material is ranked and packed into dense evidence cards.
8. Lane summaries are synthesized independently, then merged through
   intermediate nodes when the context is large.
9. The final synthesis is printed, written to `synthesis.md`, and stored with
   follow-up memory.

## Follow-Up Flow

`researchbuddy followup <run_id> "<question>"` loads `followup_memory.json` and
answers from the saved evidence instead of rerunning search or crawl. This keeps
follow-up questions cheaper and makes answers traceable to the original bundle.

## External Boundaries

ResearchBuddy talks to several external systems:

- Search providers: Exa, Tavily, or Firecrawl. One configured API key is
  required.
- Local agent harnesses: Codex by default, with Claude and Amp support behind
  `app/services/codex_exec.py`.
- Browser/runtime tools: Playwright for page capture and fallback browser
  execution.
- Media tools: `yt-dlp`, `ffmpeg`, and local Whisper for YouTube, podcast, and
  audio transcription.
- Optional local agent configs: Hermes and OpenClaw provider settings can be
  reused when present.

`researchbuddy doctor` is the public readiness check for these boundaries. It
validates provider keys, local agent auth, `uv`, `ffmpeg`, Playwright, storage,
and database paths before a long run starts.

## Persistence

ResearchBuddy stores lightweight run metadata in SQLite and stores the useful
debug/review material as files:

```text
data/storage/<run_id>/
  synthesis.md
  run.log
  followup_memory.json
  html/
  markdown/
  lanes/
  transcripts/
  youtube_transcripts.json
  podcast_transcripts.json
```

This is intentionally local-first: users can inspect, archive, or delete run
bundles without needing a hosted service.

## Release Model

The source repo is published as a Python package and can generate a separate
Homebrew tap repository with `researchbuddy tap export`. The tag-driven release
workflow runs `./scripts/release-check.sh`, builds distributions, and attaches
them to a GitHub Release. The tap formula then points at a tagged source archive
and SHA.
