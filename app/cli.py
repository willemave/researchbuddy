"""CLI entrypoint for ReviewBuddy."""

import asyncio
import subprocess
from dataclasses import dataclass
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from app.agents.base import AgentDeps
from app.cli_doctor import format_doctor_report, has_doctor_failures, run_doctor_checks
from app.cli_help import build_command_reference
from app.constants import APP_VERSION
from app.core.logging import setup_logging
from app.core.settings import get_settings
from app.models.homebrew import TapExportRequest
from app.models.review import (
    FollowupMemory,
    ReviewRunConfig,
    ReviewRunRequest,
    ReviewRunResult,
    ReviewRunStats,
)
from app.services.followup import answer_followup_question, load_followup_memory
from app.services.homebrew_tap import detect_github_remote, export_tap_repository
from app.services.setup_runtime import format_setup_report, has_setup_failures, run_setup
from app.services.storage import fetch_run, fetch_run_stats, list_runs, resolve_run_dir
from app.workflows.review import run_review

app = typer.Typer(add_completion=False)
tap_app = typer.Typer(help="Generate Homebrew tap assets.")
app.add_typer(tap_app, name="tap")
console = Console()
settings = get_settings()

OPTIONAL_PROMPT_ARGUMENT = typer.Argument(
    None,
    help="Research question or product to investigate.",
)
RUN_ID_ARGUMENT = typer.Argument(..., help="Saved run identifier")
OPTIONAL_QUESTION_ARGUMENT = typer.Argument(
    None,
    help="Follow-up question to answer from saved memory.",
)
MAX_URLS_OPTION = typer.Option(None, help="Maximum total URLs to process")
MAX_AGENTS_OPTION = typer.Option(None, help="Maximum parallel agents")
HEADFUL_OPTION = typer.Option(True, help="Allow headful fallback if headless is blocked")
TIMEOUT_OPTION = typer.Option(None, help="Navigation timeout in ms")
OUTPUT_DIR_OPTION = typer.Option(None, help="Base output directory")
PROMPT_FILE_OPTION = typer.Option(
    None,
    "--prompt-file",
    help="Read the run prompt from a UTF-8 text file.",
)
QUESTION_FILE_OPTION = typer.Option(
    None,
    "--question-file",
    help="Read the follow-up question from a UTF-8 text file.",
)
RESULT_FILE_OPTION = typer.Option(
    None,
    "--result-file",
    help="Write the final text output to an explicit file path.",
)
PLANNER_MODEL_OPTION = typer.Option(None, help="Override model for the lane planner agent")
SUB_AGENT_MODEL_OPTION = typer.Option(None, help="Override model for sub-agents")
TAP_OUTPUT_OPTION = typer.Option(None, help="Output directory for the generated Homebrew tap repo")
RUNS_LIMIT_OPTION = typer.Option(20, "--limit", min=1, help="Maximum runs to list")
STATS_OPTION = typer.Option(False, "--stats", help="Print run statistics before the synthesis")
INSTALL_PLAYWRIGHT_OPTION = typer.Option(
    True,
    "--install-playwright/--skip-playwright",
    help="Install Playwright browsers during setup",
)


@dataclass
class FollowupSessionState:
    """Cached memory for local follow-up answers."""

    run_id: str
    run_dir: Path
    prompt: str
    synthesis_markdown: str
    memory: FollowupMemory | None = None


def _read_utf8_text_file(path: Path, *, label: str) -> str:
    """Read a UTF-8 text file for CLI input.

    Args:
        path: File path to read.
        label: User-facing label for error messages.

    Returns:
        Trimmed file contents.

    Raises:
        typer.BadParameter: If the path is invalid or unreadable.
    """

    if not path.exists():
        raise typer.BadParameter(f"{label} file not found: {path}")
    if not path.is_file():
        raise typer.BadParameter(f"{label} path is not a file: {path}")
    try:
        value = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise typer.BadParameter(f"{label} file must be valid UTF-8 text: {path}") from exc
    except OSError as exc:
        raise typer.BadParameter(f"Could not read {label} file {path}: {exc}") from exc
    cleaned = value.strip()
    if not cleaned:
        raise typer.BadParameter(f"{label} file is empty: {path}")
    return cleaned


def _resolve_text_input(
    value: str | None,
    file_path: Path | None,
    *,
    field_name: str,
) -> str:
    """Resolve one explicit text input from CLI args/options.

    Args:
        value: Positional string value.
        file_path: Optional file path.
        field_name: User-facing field name.

    Returns:
        Resolved non-empty text input.

    Raises:
        typer.BadParameter: If the input is missing, duplicated, or invalid.
    """

    if value and file_path is not None:
        raise typer.BadParameter(
            f"Pass either the {field_name} argument or --{field_name}-file, not both."
        )
    if file_path is not None:
        return _read_utf8_text_file(file_path, label=field_name)
    cleaned = (value or "").strip()
    if not cleaned:
        raise typer.BadParameter(
            f"Missing {field_name}. Pass it as an argument or provide --{field_name}-file."
        )
    return cleaned


def _write_result_file(path: Path, contents: str) -> None:
    """Write CLI output to an explicit deterministic file path."""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    except OSError as exc:
        raise typer.BadParameter(f"Could not write result file {path}: {exc}") from exc


def _truncate_text(value: str, limit: int) -> str:
    """Return a single-line truncated string for CLI tables."""

    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: max(0, limit - 3)]}..."


async def _ensure_followup_memory(state: FollowupSessionState) -> FollowupMemory:
    """Load cached follow-up memory for a run when needed."""

    if state.memory is None:
        state.memory = await load_followup_memory(
            run_id=state.run_id,
            run_dir=state.run_dir,
            prompt=state.prompt,
            synthesis_markdown=state.synthesis_markdown,
        )
    return state.memory


async def _load_followup_state_for_run(
    run_id: str,
    output_dir: Path | None = None,
) -> tuple[ReviewRunResult, FollowupSessionState]:
    """Load a saved run and construct follow-up session state.

    Args:
        run_id: Saved run identifier.
        output_dir: Optional base output directory override.

    Returns:
        Tuple of the saved report and follow-up state.

    Raises:
        typer.Exit: If the run or saved synthesis cannot be found.
    """

    run_record = await fetch_run(settings.database_path, run_id)
    if run_record is None:
        console.print(f"Run not found: {run_id}")
        raise typer.Exit(code=1)

    run_dir = resolve_run_dir(run_record.output_dir, run_id, output_dir)
    synthesis_path = run_dir / "synthesis.md"
    if not synthesis_path.exists():
        console.print(f"Synthesis not found: {synthesis_path}")
        raise typer.Exit(code=1)

    synthesis_text = synthesis_path.read_text(encoding="utf-8", errors="ignore")
    total, fetched, failed = await fetch_run_stats(settings.database_path, run_id)
    report = ReviewRunResult(
        run_id=run_id,
        prompt=run_record.prompt,
        created_at=run_record.created_at,
        stats=ReviewRunStats(total_urls=total, fetched=fetched, failed=failed),
        synthesis_markdown=synthesis_text,
    )
    followup_state = FollowupSessionState(
        run_id=run_id,
        run_dir=run_dir,
        prompt=run_record.prompt,
        synthesis_markdown=synthesis_text,
    )
    return report, followup_state


@app.command()
def run(
    prompt: str | None = OPTIONAL_PROMPT_ARGUMENT,
    prompt_file: Path | None = PROMPT_FILE_OPTION,
    max_urls: int = MAX_URLS_OPTION,
    max_agents: int = MAX_AGENTS_OPTION,
    headful: bool = HEADFUL_OPTION,
    timeout_ms: int = TIMEOUT_OPTION,
    output_dir: Path = OUTPUT_DIR_OPTION,
    result_file: Path | None = RESULT_FILE_OPTION,
    planner_model: str | None = PLANNER_MODEL_OPTION,
    sub_agent_model: str | None = SUB_AGENT_MODEL_OPTION,
    stats: bool = STATS_OPTION,
) -> None:
    """Run a review research workflow."""

    setup_logging(settings.log_level)
    resolved_prompt = _resolve_text_input(prompt, prompt_file, field_name="prompt")

    config = ReviewRunConfig(
        max_urls=max_urls or settings.max_urls,
        max_agents=max_agents or settings.max_agents,
        headful=headful,
        navigation_timeout_ms=timeout_ms or settings.navigation_timeout_ms,
        output_dir=output_dir or settings.storage_path,
        planner_model=planner_model,
        sub_agent_model=sub_agent_model,
    )
    request = ReviewRunRequest(prompt=resolved_prompt, **config.model_dump())

    deps = AgentDeps(session_id="cli", job_id="cli")

    result = asyncio.run(run_review(request, deps, reporter=None))
    if result_file is not None:
        _write_result_file(result_file, result.synthesis_markdown)

    console.print(Panel.fit("ReviewBuddy complete", style="green"))
    console.print(f"Run ID: {result.run_id}")
    if result_file is not None:
        console.print(f"Result file: {result_file}", soft_wrap=True)
    if stats:
        console.print(
            f"Fetched {result.stats.fetched}/{result.stats.total_urls} URLs"
            f" ({result.stats.failed} failed)"
        )
    console.print()
    console.print(result.synthesis_markdown)


@app.command()
def commands(
    agent: bool = typer.Option(
        False,
        "--agent",
        help="Render a flatter command reference for agents and scripts",
    ),
) -> None:
    """Print a compact command reference."""

    console.print(build_command_reference(agent=agent))


@app.command()
def runs(limit: int = RUNS_LIMIT_OPTION) -> None:
    """List recent run IDs."""

    records = asyncio.run(list_runs(settings.database_path, limit=limit))
    if not records:
        console.print("No runs found.")
        return

    console.print("# Recent Runs")
    console.print()
    for record in records:
        created_at = record.created_at.astimezone().strftime("%Y-%m-%d %H:%M")
        prompt = _truncate_text(record.prompt, 72)
        console.print(f"{record.run_id}  {created_at}  {record.status}  {prompt}")


@app.command()
def doctor(
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Run setup actions before re-running doctor checks",
    ),
    install_playwright: bool = INSTALL_PLAYWRIGHT_OPTION,
) -> None:
    """Check whether the local environment is ready to run ReviewBuddy.

    Use ``--fix`` to run setup actions before printing the final doctor report.
    """

    setup_failed = False
    if fix:
        result = run_setup(settings, install_playwright=install_playwright)
        console.print(format_setup_report(result.actions))
        console.print()
        checks = result.doctor_checks
        setup_failed = has_setup_failures(result.actions)
    else:
        checks = run_doctor_checks(settings)
    console.print(format_doctor_report(checks))
    if setup_failed or has_doctor_failures(checks):
        raise typer.Exit(code=1)


@app.command()
def setup(
    install_playwright: bool = INSTALL_PLAYWRIGHT_OPTION,
) -> None:
    """Prepare the local environment to run ReviewBuddy."""

    result = run_setup(settings, install_playwright=install_playwright)
    console.print(format_setup_report(result.actions))
    console.print()
    console.print(format_doctor_report(result.doctor_checks))
    if has_setup_failures(result.actions) or has_doctor_failures(result.doctor_checks):
        raise typer.Exit(code=1)


@app.command()
def ask(
    run_id: str = RUN_ID_ARGUMENT,
    question: str | None = OPTIONAL_QUESTION_ARGUMENT,
    question_file: Path | None = QUESTION_FILE_OPTION,
    output_dir: Path = OUTPUT_DIR_OPTION,
    result_file: Path | None = RESULT_FILE_OPTION,
    sub_agent_model: str | None = SUB_AGENT_MODEL_OPTION,
) -> None:
    """Answer a follow-up question from a previous session."""

    setup_logging(settings.log_level)
    resolved_question = _resolve_text_input(question, question_file, field_name="question")

    async def _run() -> None:
        _report, followup_state = await _load_followup_state_for_run(run_id, output_dir)
        memory = await _ensure_followup_memory(followup_state)
        answer = await answer_followup_question(
            memory,
            resolved_question,
            model_name=sub_agent_model,
        )
        if result_file is not None:
            _write_result_file(result_file, answer)
            console.print(f"Result file: {result_file}", soft_wrap=True)
        console.print(answer)

    asyncio.run(_run())


@tap_app.command("export")
def export_tap(
    output_dir: Path | None = TAP_OUTPUT_OPTION,
    github_owner: str | None = typer.Option(None, help="GitHub owner for source and tap repos"),
    source_repo: str | None = typer.Option(None, help="Source repository name"),
    tap_repo: str = typer.Option("homebrew-reviewbuddy", help="Tap repository name"),
) -> None:
    """Generate a Homebrew tap repository for ReviewBuddy."""

    repo_root = Path(__file__).resolve().parents[1]
    remote = detect_github_remote(repo_root)
    resolved_owner = github_owner
    resolved_source_repo = source_repo
    if remote is not None:
        resolved_owner = resolved_owner or remote[0]
        resolved_source_repo = resolved_source_repo or remote[1]

    if not resolved_owner or not resolved_source_repo:
        console.print("Could not infer the GitHub owner/repo from git remote origin.")
        console.print("Pass --github-owner and --source-repo explicitly.")
        raise typer.Exit(code=1)

    target_output_dir = output_dir or (repo_root.parent / tap_repo)
    request = TapExportRequest(
        output_dir=target_output_dir,
        github_owner=resolved_owner,
        source_repo=resolved_source_repo,
        tap_repo=tap_repo,
        version=APP_VERSION,
        app_description="AI-powered review research assistant with parallel crawling and synthesis",
    )
    result = export_tap_repository(request)

    if not (result.output_dir / ".git").exists():
        subprocess.run(
            ["git", "init", "-b", "main", str(result.output_dir)],
            check=True,
            capture_output=True,
            text=True,
        )

    console.print(Panel.fit("ReviewBuddy tap repository exported", style="green"))
    console.print(f"Output: {result.output_dir}")
    for path in result.files:
        console.print(f"- {path.relative_to(result.output_dir)}")


def main() -> None:
    """CLI entrypoint."""

    app()


if __name__ == "__main__":
    main()
