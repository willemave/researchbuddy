# ResearchBuddy Commands

Primary entry points:
- `researchbuddy`
- `scripts/researchbuddy`

## `researchbuddy start "<prompt>" [--json]`
- Starts a new research run in the background.
- Makes the new run current.
- Refuses to start if another run has a live worker process.
- Prints the run ID, PID, log path, and exact `status` / `watch` commands.
- Use `--json` for machine-readable startup output.

## `researchbuddy status [--run-id RUN_ID] [--json]`
- Prints current run status by default.
- Shows PID health, URL counts, output directory, log path, and synthesis path.
- Use `--json` for agents and scripts.

## `researchbuddy watch [--run-id RUN_ID] [--interval SECONDS] [--timeout SECONDS]`
- Streams the current worker log and waits until the run completes or fails.
- Exits non-zero when the worker process disappears while the run is still in progress.
- Exits zero on completion and non-zero on failure.

## `researchbuddy followup "<question>" [--run-id RUN_ID]`
- Answers a follow-up question from persisted run memory.
- Defaults to the current run.
- Does not re-crawl or re-download sources.

## `researchbuddy doctor [--fix] [--skip-playwright]`
- Validates required API keys, binaries, Codex auth, Playwright browser launch, writable storage paths, and current-run health.
- Use `--fix` when local setup or stale run records should be repaired before the final doctor report.
- If it fails on a dependency such as `ffmpeg`, read `references/troubleshooting.md`.

## `researchbuddy list [--limit 20] [--json]`
- Lists recent saved runs.
- Marks the current run in human output.
- Use `--json` for agents and scripts.
