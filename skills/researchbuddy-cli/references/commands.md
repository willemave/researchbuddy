# ResearchBuddy Commands

Primary entry points:
- `researchbuddy`
- `scripts/researchbuddy`

## `researchbuddy run "<prompt>" [--stats]`
- Executes a new one-shot research run.
- Writes artifacts under `data/storage/<run_id>/`.
- For long runs in an agent session, prefer a background launch such as:
  `scripts/researchbuddy run "<prompt>" > /tmp/researchbuddy.log 2>&1 & echo $!`
- `--stats` is optional and only prints fetched/failed URL counts when explicitly requested.

## `researchbuddy followup <run_id> "<question>"`
- Answers a follow-up question from persisted run memory.
- Does not re-crawl or re-download sources.

## `researchbuddy commands [--agent]`
- Prints a compact command reference.
- Use `--agent` for the flatter machine-readable variant.

## `researchbuddy doctor [--fix] [--skip-playwright]`
- Validates required API keys, binaries, Codex auth, Playwright browser launch, and writable storage paths.
- Use `--fix` when local setup should be repaired before the final doctor report.
- If it fails on a dependency such as `ffmpeg`, read `references/troubleshooting.md`.
- Run this before handing the tool to another bot.
