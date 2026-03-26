# ReviewBuddy Commands

Primary entry points:
- `reviewbuddy`
- `scripts/reviewbuddy`

## `reviewbuddy run "<prompt>" [--stats]`
- Executes a new one-shot research run.
- Writes artifacts under `data/storage/<run_id>/`.
- For long runs in an agent session, prefer a background launch such as:
  `scripts/reviewbuddy run "<prompt>" > /tmp/reviewbuddy.log 2>&1 & echo $!`
- `--stats` is optional and only prints fetched/failed URL counts when explicitly requested.

## `reviewbuddy ask <run_id> "<question>"`
- Answers a follow-up question from persisted run memory.
- Does not re-crawl or re-download sources.

## `reviewbuddy commands [--agent]`
- Prints a compact command reference.
- Use `--agent` for the flatter machine-readable variant.

## `reviewbuddy doctor [--fix] [--skip-playwright]`
- Validates required API keys, binaries, Codex auth, Playwright browser launch, and writable storage paths.
- Use `--fix` when local setup should be repaired before the final doctor report.
- If it fails on a dependency such as `ffmpeg`, read `references/troubleshooting.md`.
- Run this before handing the tool to another bot.
