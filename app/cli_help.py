"""Shared CLI help text for users and agents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CliCommandHelp:
    """Structured help for one CLI command."""

    name: str
    usage: str
    summary: str
    details: tuple[str, ...]
    examples: tuple[str, ...]


CLI_COMMANDS: tuple[CliCommandHelp, ...] = (
    CliCommandHelp(
        name="run",
        usage='reviewbuddy run "<prompt>" [--result-file answer.md] [--stats]',
        summary="Execute a new one-shot research run and print the synthesis.",
        details=(
            "Runs planning, search, crawl, synthesis, and writes artifacts under data/storage/<run_id>/.",
            "Use the positional prompt for normal CLI usage.",
            "Use --prompt-file only when you explicitly want to read the prompt from a UTF-8 text file.",
            "Use --result-file when you want the final synthesis at a deterministic path.",
            "Use --stats when you also want the fetched/failed URL counts printed in the terminal output.",
            "Best when you want a final answer in a single command.",
        ),
        examples=(
            'reviewbuddy run "best dishwasher for quiet apartment"',
            "reviewbuddy run --prompt-file prompt.txt --result-file output/synthesis.md",
        ),
    ),
    CliCommandHelp(
        name="ask",
        usage='reviewbuddy ask <run_id> "<question>" [--result-file answer.txt]',
        summary="Answer a follow-up question from a saved run without re-crawling.",
        details=(
            "Loads persisted follow-up memory from the saved session.",
            "Use the positional question for normal CLI usage.",
            "Use --question-file only when you explicitly want to read the question from a UTF-8 text file.",
            "Use --result-file when you want the answer written to a deterministic path.",
            "Useful for previous-session Q&A in scripts or agent workflows.",
        ),
        examples=(
            'reviewbuddy ask abc123 "What were the main warranty concerns?"',
            "reviewbuddy ask abc123 --question-file question.txt --result-file answer.txt",
        ),
    ),
    CliCommandHelp(
        name="commands",
        usage="reviewbuddy commands [--agent]",
        summary="Print a compact command reference.",
        details=(
            "Use --agent for a flatter, machine-friendly reference format.",
            "Points to the markdown reference files under docs/.",
        ),
        examples=("reviewbuddy commands --agent",),
    ),
    CliCommandHelp(
        name="runs",
        usage="reviewbuddy runs [--limit 20]",
        summary="List recent saved runs so you can grab a run ID for follow-up commands.",
        details=(
            "Reads the recent run history from the local SQLite database.",
            "Outputs run ID, created time, status, and a truncated prompt summary.",
        ),
        examples=("reviewbuddy runs --limit 10",),
    ),
    CliCommandHelp(
        name="setup",
        usage="reviewbuddy setup [--skip-playwright]",
        summary="Prepare the local machine to run the CLI, then rerun doctor checks.",
        details=(
            "Persists detected search-provider settings into the local .env when possible.",
            "Creates the storage/database paths and optionally installs Playwright browsers.",
        ),
        examples=("reviewbuddy setup",),
    ),
    CliCommandHelp(
        name="doctor",
        usage="reviewbuddy doctor",
        summary="Check whether the current machine is ready to run the CLI.",
        details=(
            "Validates required API keys, required binaries, and writable storage paths.",
            "Use this before handing the tool to another bot or promoting a runtime to production.",
        ),
        examples=("reviewbuddy doctor",),
    ),
    CliCommandHelp(
        name="tap export",
        usage="reviewbuddy tap export [--output-dir PATH]",
        summary="Generate a Homebrew tap repository for publishing ReviewBuddy.",
        details=(
            "Writes Formula/, README.md, a validation workflow, and a tap-maintainer skill.",
            "Defaults to the GitHub origin remote and writes to ../homebrew-reviewbuddy when possible.",
        ),
        examples=("reviewbuddy tap export",),
    ),
)

CLI_REFERENCE_PATH = "docs/cli-reference.md"
AGENT_REFERENCE_PATH = "docs/agent-cli-reference.md"


def build_command_reference(*, agent: bool = False) -> str:
    """Build CLI reference text.

    Args:
        agent: Whether to render a flatter agent-oriented format.

    Returns:
        Markdown command reference.
    """

    if agent:
        return _build_agent_reference()
    return _build_user_reference()


def _build_user_reference() -> str:
    lines = [
        "# ReviewBuddy CLI",
        "",
        "Primary entry points:",
        "- Installed command: `reviewbuddy`",
        "- Local wrapper: `scripts/reviewbuddy`",
        "",
        "Commands:",
    ]
    for command in CLI_COMMANDS:
        lines.extend(
            [
                f"## `{command.usage}`",
                command.summary,
                "",
                *[f"- {detail}" for detail in command.details],
                "",
                "Example:",
                *[f"- `{example}`" for example in command.examples],
                "",
            ]
        )
    lines.extend(
        [
            "Reference files:",
            f"- `{CLI_REFERENCE_PATH}`",
            f"- `{AGENT_REFERENCE_PATH}`",
        ]
    )
    return "\n".join(lines).strip()


def _build_agent_reference() -> str:
    lines = [
        "# ReviewBuddy CLI For Agents",
        "",
        "Entrypoints:",
        "- `reviewbuddy`",
        "- `scripts/reviewbuddy`",
        "",
    ]
    for command in CLI_COMMANDS:
        lines.extend(
            [
                f"## {command.name}",
                f"Usage: `{command.usage}`",
                f"Purpose: {command.summary}",
                "Behavior:",
                *[f"- {detail}" for detail in command.details],
                "Example:",
                *[f"- `{example}`" for example in command.examples],
                "",
            ]
        )
    lines.extend(
        [
            "Docs:",
            f"- `{CLI_REFERENCE_PATH}`",
            f"- `{AGENT_REFERENCE_PATH}`",
        ]
    )
    return "\n".join(lines).strip()
