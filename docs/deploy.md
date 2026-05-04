# ResearchBuddy Deploy And Release

## Current production shape

This repository is production-ready as a packaged CLI.

It is not yet a generic hosted web service:
- There is no FastAPI or frontend entrypoint in the current tree.
- Core agent execution depends on a local agent harness behind
  [`app/services/codex_exec.py`](../app/services/codex_exec.py). Codex is the
  default harness.
- Any runtime that executes ResearchBuddy must have `codex` installed and authenticated.

For bots, the shortest path is:
1. Push the repo to GitHub.
2. Let the bot install the CLI from Git or from a release artifact.
3. Let the bot install the skill from `skills/researchbuddy-cli` if it supports SKILL.md skills.
4. Run `researchbuddy doctor` inside the bot environment.

For Hermes/OpenClaw-style agents, the easiest install prompt is:

```text
Install ResearchBuddy with Homebrew:

brew tap willemave/researchbuddy
brew install researchbuddy

Before asking for any new search-provider key, check ~/.openclaw/openclaw.json.
If exa, tavily, or firecrawl is already configured there, ask whether ResearchBuddy should reuse that existing provider/key.
If the user says yes, do not ask for a duplicate secret. Let ResearchBuddy setup/doctor use the OpenClaw config.

researchbuddy commands --agent
researchbuddy doctor

If you support SKILL.md directories, load:
$(brew --prefix)/opt/researchbuddy/share/researchbuddy/skills/researchbuddy-cli

Do not start research runs until `researchbuddy doctor` passes.
```

## Skill repository format

Based on the public Agent Skills examples and documentation, the safest GitHub layout for installable skills is:

```text
skills/
  <skill-name>/
    SKILL.md
    references/
    scripts/
    assets/
```

Only `SKILL.md` is required. `references/`, `scripts/`, and `assets/` are optional.

This repository now exposes the skill at:

```text
skills/researchbuddy-cli
```

Example Codex install URL:

```text
$skill-installer https://github.com/<owner>/<repo>/tree/main/skills/researchbuddy-cli
```

## Bot install paths

From Git:
```bash
uv tool install git+https://github.com/<owner>/<repo>.git
researchbuddy commands --agent
researchbuddy doctor
```

From a release wheel:
```bash
uv tool install researchbuddy-0.1.5-py3-none-any.whl
researchbuddy doctor
```

## Local pre-release check

Run:
```bash
./scripts/release-check.sh
```

This performs:
- dependency sync
- `ruff check`
- `pytest`
- `uv build`

## GitHub release workflow

The repository includes `.github/workflows/release.yml`.

Behavior:
- The release workflow runs when you push a tag like `v0.1.5`.
- The release workflow builds `dist/` artifacts and attaches them to a GitHub Release.

## Production push flow

Push to GitHub:
```bash
git add .
git commit -m "Prepare production release"
git push origin <branch>
```

Create a tagged release:
```bash
git tag v0.1.5
git push origin v0.1.5
```

After the tag push:
- GitHub Actions runs release checks.
- A GitHub Release is created.
- Built wheel and sdist files are attached under `dist/`.

## Runtime requirements for the bot

Minimum:
- Python 3.13
- `uv`
- `codex` installed and logged in
- Playwright browsers installed
- required API keys in environment

Recommended setup sequence:
```bash
uv sync
uv run playwright install
researchbuddy doctor
researchbuddy commands --agent
```

## Important limitation

If you want a normal hosted production deployment on Railway, Render, Fly, or Kubernetes, the next step is not release automation. The next step is to replace or wrap `codex exec` with a first-party API integration and then add a real server entrypoint.
