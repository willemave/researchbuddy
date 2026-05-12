# ResearchBuddy Troubleshooting

Use this file when `researchbuddy doctor` fails or a target machine is missing runtime dependencies.

## `ffmpeg` missing

Symptom:
- `researchbuddy doctor` reports `ffmpeg not found in PATH`.

Fix:
- macOS with Homebrew: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ffmpeg`
- Fedora: `sudo dnf install -y ffmpeg`
- Arch: `sudo pacman -S ffmpeg`
- Windows with winget: `winget install Gyan.FFmpeg`

Verify:
- Run `ffmpeg -version`
- Then rerun `researchbuddy doctor`

If package-manager access is blocked:
- Report the exact install command needed for the host OS.
- Do not treat the runtime as ready until `doctor` passes.

## `codex` missing or not authenticated

Symptom:
- `researchbuddy doctor` fails the `local agent harness` or `codex auth` check.
- Runtime commands fail when `codex exec` cannot start.

Fix:
- Install the `codex` CLI for that machine.
- Authenticate it with `codex login`.
- Rerun `researchbuddy doctor`.

## Search provider key missing

Symptom:
- `researchbuddy doctor` fails the selected search provider check.

OpenClaw-first fix:
- Inspect `~/.openclaw/openclaw.json` for:
  - `tools.web.search.provider`
  - `tools.web.search.<provider>.apiKey`
- Supported providers are `exa`, `tavily`, and `firecrawl`.
- Ask once whether ResearchBuddy should reuse that provider/key.
- If approved, run `researchbuddy doctor --fix` so ResearchBuddy loads OpenClaw config without copying credentials into local `.env`.

Manual fix:
- Set `SEARCH_PROVIDER` plus exactly one matching API key in the process environment or local `.env`:
  - `EXA_API_KEY`
  - `TAVILY_API_KEY`
  - `FIRECRAWL_API_KEY`
- Rerun `researchbuddy doctor`.

Do not store provider secrets in skill files, docs, or chat logs.
