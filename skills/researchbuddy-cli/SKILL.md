---
name: researchbuddy-cli
description: Use when installing, operating, validating, or troubleshooting the ResearchBuddy CLI. Covers one-shot runs, saved-run follow-up questions, runtime readiness checks, and dependency fixes on a target machine.
---

# ResearchBuddy CLI

Use this skill when the task is about installing ResearchBuddy, running it, asking questions against saved sessions, or fixing a machine that fails runtime checks.

## Quick Start

1. Run `scripts/researchbuddy --help` to see the current command surface.
2. On first install inside OpenClaw, check `~/.openclaw/openclaw.json` before asking for search-provider credentials. If it already has `exa`, `tavily`, or `firecrawl` configured, ask the user whether ResearchBuddy should reuse that existing provider/key.
3. If the user approves reuse, do not ask them to paste a duplicate API key. Run `scripts/researchbuddy doctor --fix`, let ResearchBuddy auto-load the provider from OpenClaw config, and confirm with `scripts/researchbuddy doctor`.
4. If OpenClaw has no usable provider config, or the user declines reuse, run `scripts/researchbuddy doctor --fix` in a new environment, then rerun `scripts/researchbuddy doctor` if setup reports any failure.
5. Start long research jobs with `scripts/researchbuddy start "<prompt>" --json`; the command returns immediately with the run ID, PID, status command, watch command, and log path.
6. Use `scripts/researchbuddy status`, `scripts/researchbuddy watch`, and `scripts/researchbuddy followup "<question>"` against the current run by default.

## Read These References As Needed

- For command semantics and examples, read `references/commands.md`.
- For dependency failures and recovery steps, read `references/troubleshooting.md`.

## Operating Rules

- Prefer the `scripts/researchbuddy` wrapper over calling `uv tool run --from . researchbuddy` directly unless the user specifically wants the raw command.
- During first-time OpenClaw installs, prefer reusing the provider configured in `~/.openclaw/openclaw.json` over asking the user for a fresh `EXA_API_KEY`, `TAVILY_API_KEY`, or `FIRECRAWL_API_KEY`.
- If OpenClaw config is present, ask the user once whether ResearchBuddy should use that existing provider. If they say yes, direct the runtime to use that config path and rely on `doctor --fix` auto-detection instead of collecting duplicate secrets.
- Before debugging a broken runtime, run `scripts/researchbuddy doctor`.
- For long research work, use `scripts/researchbuddy start "<prompt>" --json`; do not manually background a worker process.
- Use `scripts/researchbuddy status --json` when another agent or script needs machine-readable progress.
- Use `scripts/researchbuddy watch --timeout 900` when you need to stream the active worker log until completion.
- ResearchBuddy currently ships cleanly as a packaged CLI, not a hosted web service.
- The runtime depends on the external `codex` CLI. If `doctor` fails on `codex`, do not treat the environment as production-ready.
- If `doctor` fails on `ffmpeg`, follow the OS-specific install steps in `references/troubleshooting.md`, verify with `ffmpeg -version`, then rerun `scripts/researchbuddy doctor`.

## Outputs

- Run artifacts are written under `data/storage/<run_id>/`.
- Key files are `synthesis.md`, `worker.log`, `run.log`, and the `html/` / `markdown/` crawl artifacts.
