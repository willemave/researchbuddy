## Application Overview

ResearchBuddy is a local-first AI research CLI. It turns broad questions into
parallel research lanes, searches and crawls sources, compresses source material
into evidence cards, and synthesizes cited markdown reports.

**Key Components:**
- **CLI** (`app/cli.py`): Typer commands for runs, follow-ups, inspection, setup, doctor checks, transcription, and tap export
- **Workflow** (`app/workflows/review.py`): run orchestration, lane execution, crawling, evidence packing, and synthesis
- **Agents** (`app/agents/`): lane planning, lane refinement, lane synthesis, merge synthesis, and final synthesis prompts
- **Services** (`app/services/`): search providers, local agent execution, Playwright crawling, transcription, storage, setup, and Homebrew tap rendering
- **Models** (`app/models/`): Pydantic v2 request/response models and persisted run data

**Workflows:**
| Type | Flow |
|------|------|
| Research run | prompt -> lane plan -> search/crawl/refine -> evidence cards -> lane summaries -> final synthesis |
| Follow-up | saved run -> follow-up memory -> answer from stored evidence |
| Transcription | YouTube, podcast, or local audio -> local Whisper transcript |
| Release | version bump -> release checks -> GitHub tag -> Homebrew tap SHA update |

See [docs/architecture.md](docs/architecture.md) for the technical architecture.

---

## 1. Python CLI Coding Rules

* Prefer **functions over classes** unless a Pydantic model, dataclass, or command type makes state/contracts clearer.
* Use **full type hints** and validate boundaries with **Pydantic v2** models.
* Keep command handlers thin; push behavior into services/workflows that can be tested directly.
* Use RORO-style functions where payloads are structured.
* Use `lower_snake_case` for files/dirs; use verb-style booleans such as `is_valid` and `has_permission`.
* Use guard-clause error handling and early returns over nested `else`.
* Use Google-style docstrings for public functions/classes.
* Define constants in `app/constants.py` or module-level UPPER_CASE.

---

## 2. Runtime Boundaries

* No hardcoded secrets; use `app/core/settings.py` and `pydantic-settings`.
* Validate inputs at CLI, settings, external-service, and persistence boundaries.
* Never build SQL with f-strings; use parameterized queries.
* Treat network, browser, transcript, and local-agent execution failures as expected runtime states with useful error messages.
* Keep local-agent execution behind `app/services/codex_exec.py`; do not scatter subprocess calls through the workflow.
* Keep user-facing setup checks in `doctor`/`setup` so install failures are diagnosable before a long run starts.

---

## 3. Testing Requirements

* Write tests for all new behavior in `app/tests/` using idiomatic pytest.
* Mirror the touched module when naming tests where practical: `test_<module_name>.py`.
* Prefer focused unit tests for services and prompt builders; use workflow tests for integration behavior.
* Mock external providers, browser work, local agents, and transcription.
* Run tests with:
  ```bash
  uv run pytest app/tests/ -v
  ```
* Use fixtures/factories for test data. Never use production data.

---

## 4. Development Workflow

* Use `uv` for dependency and environment management.
* Keep `.env.example` current; never commit `.env`.
* Before handoff after Python changes, run `uv run ruff check .` and fix violations.
* For broader changes, also run `uv run pytest app/tests/ -q`.
* If asked to "commit and push" changes that should ship through Homebrew/tap, also bump the app version in `pyproject.toml` and `app/constants.py`, create/push a new git tag, and update the tap formula to point at the new tagged release and SHA.

---

## 5. Package & Dev Tools

### Package Management
```bash
uv sync                    # Install dependencies
uv add <package>           # Add dependency
uv add --dev <package>     # Add dev dependency
source .venv/bin/activate  # Activate venv
```

### Code Quality
```bash
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run pytest app/tests/ -v
```

### Running The CLI
```bash
uv sync
uv run playwright install
cp .env.example .env       # Add one search-provider API key
uv run researchbuddy doctor
uv run researchbuddy run "your research question"
```

Useful commands:
```bash
uv run researchbuddy commands --agent
uv run researchbuddy followup <run_id> "question"
uv run researchbuddy inspect <run_id> --sources --lanes --transcripts
uv run researchbuddy tap export
./scripts/release-check.sh
```

---

## 6. Preferred Dev Tools

* **LLM internet search**: Use the EXA MCP `web_search_exa` tool for web/internet lookups when available.
* **LLM code search**: Use the Morph MCP `warp_grep` tool for repository code searches when available; otherwise use `rg`.

| Tool | Purpose | Example |
|------|---------|---------|
| **fd** | Fast file finder | `fd -e py foo` |
| **rg** | Fast code search | `rg "TODO"` |
| **ast-grep (sg)** | AST-aware search | `sg -p 'if ($A) { $B }'` |
| **jq** | JSON processor | `cat data.json | jq '.items'` |
| **bat** | Better cat | `bat file.py` |
| **httpie** | HTTP client | `http GET api/foo` |

**Keep replies short, technical, and complete.**

**Always run `ruff check` on touched Python files or the repo after a set of changes, and fix violations before final handoff whenever possible.**
