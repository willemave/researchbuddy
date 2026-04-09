# ResearchBuddy CLI For Agents

Entrypoints:
- `researchbuddy`
- `scripts/researchbuddy`

## run
Usage: `researchbuddy run "<prompt>" [--mode auto|product|restaurant|research] [--stats]`
Purpose: Execute a new one-shot research run and print the synthesis.
Behavior:
- Runs planning, search, crawl, synthesis, and writes artifacts under `data/storage/<run_id>/`.
- Use `--mode` to force product-review, restaurant, or general-research behavior instead of automatic prompt inference.
- Use `--stats` when you also want the fetched/failed URL counts printed in the terminal output.
- Best when you want a final answer in a single command.
Example:
- `researchbuddy run "best dishwasher for quiet apartment"`
- `researchbuddy run "best sushi in portland" --mode restaurant`

## inspect
Usage: `researchbuddy inspect <run_id> [--sources] [--lanes] [--transcripts]`
Purpose: Inspect saved artifacts for a run without re-running the workflow.
Behavior:
- Prints the saved run metadata and output directory.
- Use `--sources` to list stored source URLs and statuses.
- Use `--lanes` to list saved lane markdown files.
- Use `--transcripts` to list saved YouTube and podcast transcript metadata.
Example:
- `researchbuddy inspect abc123 --sources --transcripts`

## followup
Usage: `researchbuddy followup <run_id> "<question>"`
Purpose: Answer a follow-up question from a saved run without re-crawling.
Behavior:
- Use `researchbuddy runs` first when you need to look up the saved run ID.
- Loads persisted follow-up memory from the saved session.
- Useful for previous-session Q&A in scripts or agent workflows.
Example:
- `researchbuddy followup abc123 "What were the main warranty concerns?"`

## commands
Usage: `researchbuddy commands [--agent]`
Purpose: Print a compact command reference.
Behavior:
- Use `--agent` for a flatter, machine-friendly reference format.
- Points to the markdown reference files under `docs/`.
Example:
- `researchbuddy commands --agent`

## transcribe
Usage: `researchbuddy transcribe <source> [--type auto|youtube|podcast|audio]`
Purpose: Transcribe one local audio file or supported URL with local Whisper.
Behavior:
- Accepts local audio files, YouTube URLs, and podcast URLs.
- Use `--type` when auto-detection is ambiguous.
- Prints the transcript to stdout and can also write it to `--result-file`.
Example:
- `researchbuddy transcribe ./episode.mp3 --type audio`

## setup
Usage: `researchbuddy setup [--skip-playwright]`
Purpose: Prepare the local machine to run the CLI, then rerun doctor checks.
Behavior:
- Persists detected search-provider settings into the local `.env` when possible.
- In OpenClaw environments, agents should first check `~/.openclaw/openclaw.json` and ask whether ResearchBuddy should reuse an existing `exa`, `tavily`, or `firecrawl` provider before requesting new credentials.
- Creates the storage/database paths and optionally installs Playwright browsers.
Example:
- `researchbuddy setup`

## doctor
Usage: `researchbuddy doctor [--fix] [--skip-playwright]`
Purpose: Check whether the current machine is ready to run the CLI, and optionally fix local setup gaps.
Behavior:
- Validates required API keys, required binaries, Codex auth, Playwright browser launch, and writable storage paths.
- Use `--fix` to run setup before the final report when local dependencies need remediation.
- Use this before handing the tool to another bot or promoting a runtime to production.
Example:
- `researchbuddy doctor`
- `researchbuddy doctor --fix`

## tap export
Usage: `researchbuddy tap export [--output-dir PATH]`
Purpose: Generate a Homebrew tap repository for publishing ResearchBuddy.
Behavior:
- Writes `Formula/`, `README.md`, a validation workflow, and a tap-maintainer skill.
- Defaults to the GitHub origin remote and writes to `../homebrew-researchbuddy` when possible.
Example:
- `researchbuddy tap export`
