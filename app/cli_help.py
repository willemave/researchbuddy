"""Shared CLI help text for users and agents."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from difflib import get_close_matches


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
        usage='researchbuddy run "<prompt>" [--mode auto|product|restaurant|research] [--result-file answer.md] [--stats]',
        summary="Execute a new one-shot research run and print the synthesis.",
        details=(
            "Runs planning, search, crawl, synthesis, and writes artifacts under data/storage/<run_id>/.",
            "Use --mode to force product-review, restaurant, or general-research behavior instead of automatic prompt inference.",
            "Prints the run ID and final synthesis to stdout, and can also write the synthesis to --result-file.",
            "Prints a ChatGPT continuation link based on the final synthesis so you can continue the conversation there.",
            "Use the positional prompt for normal CLI usage.",
            "Use --prompt-file only when you explicitly want to read the prompt from a UTF-8 text file.",
            "Use --result-file when you want the final synthesis at a deterministic path.",
            "Use --stats when you also want the fetched/failed URL counts printed in the terminal output.",
            "Best when you want a final answer in a single command.",
        ),
        examples=(
            'researchbuddy run "best dishwasher for quiet apartment"',
            'researchbuddy run "best sushi in portland" --mode restaurant',
            "researchbuddy run --prompt-file prompt.txt --result-file output/synthesis.md",
        ),
    ),
    CliCommandHelp(
        name="inspect",
        usage="researchbuddy inspect <run_id> [--sources] [--lanes] [--transcripts]",
        summary="Inspect saved artifacts for a run without rerunning the workflow.",
        details=(
            "Prints the saved run metadata and output directory.",
            "Use --sources to list stored source URLs and statuses.",
            "Use --lanes to list saved lane markdown files.",
            "Use --transcripts to list saved YouTube and podcast transcript metadata.",
        ),
        examples=(
            "researchbuddy inspect abc123",
            "researchbuddy inspect abc123 --sources --transcripts",
        ),
    ),
    CliCommandHelp(
        name="followup",
        usage='researchbuddy followup <run_id> "<question>" [--result-file answer.txt]',
        summary="Answer a follow-up question from a saved run without re-crawling.",
        details=(
            "Pass the saved <run_id> as the first argument. Use researchbuddy runs when you need to look one up.",
            "Loads persisted follow-up memory from the saved session.",
            "Prints the follow-up answer to stdout, and can also write the answer to --result-file.",
            "Prints a ChatGPT continuation link based on the answer so you can keep the thread going in ChatGPT.",
            "Use the positional question for normal CLI usage.",
            "Use --question-file only when you explicitly want to read the question from a UTF-8 text file.",
            "Use --result-file when you want the answer written to a deterministic path.",
            "Useful for previous-session Q&A in scripts or agent workflows.",
        ),
        examples=(
            'researchbuddy followup abc123 "What were the main warranty concerns?"',
            "researchbuddy followup abc123 --question-file question.txt --result-file answer.txt",
        ),
    ),
    CliCommandHelp(
        name="commands",
        usage="researchbuddy commands [--agent]",
        summary="Print a command reference with usage, behavior, and examples for every CLI command.",
        details=(
            "Use --agent for a flatter, machine-friendly reference format.",
            "Returns enough detail to drive scripts or agents without opening the docs first.",
            "Points to the markdown reference files under docs/ for the longer reference text.",
        ),
        examples=("researchbuddy commands --agent",),
    ),
    CliCommandHelp(
        name="transcribe",
        usage="researchbuddy transcribe <source> [--type auto|youtube|podcast|audio] [--result-file transcript.txt]",
        summary="Transcribe one local audio file or supported URL with local Whisper.",
        details=(
            "Accepts local audio files, YouTube URLs, and podcast URLs.",
            "Use --type when auto-detection is ambiguous.",
            "Prints the transcript to stdout and can also write it to --result-file.",
        ),
        examples=(
            "researchbuddy transcribe ./episode.mp3 --type audio",
            'researchbuddy transcribe "https://www.youtube.com/watch?v=abc123"',
        ),
    ),
    CliCommandHelp(
        name="runs",
        usage="researchbuddy runs [--limit 20]",
        summary="List recent saved runs so you can grab a run ID for follow-up commands.",
        details=(
            "Reads the recent run history from the local SQLite database.",
            "Outputs run ID, created time, status, and a truncated prompt summary.",
            "Use this when you need to find a prior run before calling researchbuddy followup.",
        ),
        examples=("researchbuddy runs --limit 10",),
    ),
    CliCommandHelp(
        name="setup",
        usage="researchbuddy setup [--skip-playwright]",
        summary="Prepare the local machine to run the CLI, then rerun doctor checks.",
        details=(
            "Persists detected search-provider settings into the local .env when possible.",
            "Creates the storage/database paths and optionally installs Playwright browsers.",
            "Prints both the setup report and a follow-up doctor report, then exits non-zero if readiness problems remain.",
        ),
        examples=("researchbuddy setup",),
    ),
    CliCommandHelp(
        name="doctor",
        usage="researchbuddy doctor [--fix] [--skip-playwright]",
        summary="Check whether the current machine is ready to run the CLI, and optionally fix local setup gaps.",
        details=(
            "Validates required API keys, required binaries, Codex auth, Playwright browser launch, and writable storage paths.",
            "Use --fix to run the setup flow first so local storage, config, and Playwright browsers are repaired before the final report.",
            "Use this before handing the tool to another bot or promoting a runtime to production.",
            "Prints a full readiness report and exits non-zero when setup or runtime checks fail.",
        ),
        examples=("researchbuddy doctor", "researchbuddy doctor --fix"),
    ),
    CliCommandHelp(
        name="tap export",
        usage="researchbuddy tap export [--output-dir PATH]",
        summary="Generate a Homebrew tap repository for publishing ResearchBuddy.",
        details=(
            "Writes Formula/, README.md, a validation workflow, and a tap-maintainer skill.",
            "Defaults to the GitHub origin remote and writes to ../homebrew-researchbuddy when possible.",
            "Prints the export directory and the files written so a release bot can continue without extra discovery.",
        ),
        examples=("researchbuddy tap export",),
    ),
)

CLI_REFERENCE_PATH = "docs/cli-reference.md"
AGENT_REFERENCE_PATH = "docs/agent-cli-reference.md"
RENAMED_COMMANDS: dict[str, str] = {"ask": "followup"}
CLI_COMMANDS_BY_NAME = {command.name: command for command in CLI_COMMANDS}


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


def get_command_help(name: str) -> CliCommandHelp | None:
    """Return shared help metadata for one command."""

    return CLI_COMMANDS_BY_NAME.get(name)


def suggest_command_names(
    value: str,
    *,
    limit: int = 3,
    available_commands: Sequence[str] | None = None,
) -> tuple[str, ...]:
    """Return the best available command suggestions for a bad command name."""

    if value in RENAMED_COMMANDS:
        return (RENAMED_COMMANDS[value],)

    searchable = tuple(available_commands or CLI_COMMANDS_BY_NAME)
    matches = get_close_matches(value, searchable, n=limit, cutoff=0.34)
    if matches:
        return tuple(matches)
    return searchable[:limit]


def build_command_guidance(command_name: str, *, reason: str | None = None) -> str:
    """Build guided help text for a specific command."""

    command = get_command_help(command_name)
    if command is None:
        fallback_reason = reason or f"No help found for command '{command_name}'."
        return "\n".join(
            (fallback_reason, "", "Use `researchbuddy --help` for the full command list.")
        )

    lines: list[str] = []
    if reason:
        lines.extend((reason, ""))
    lines.extend(
        (
            f"Usage: {command.usage}",
            command.summary,
            "",
            "Details:",
            *[f"- {detail}" for detail in command.details],
            "",
            "Examples:",
            *[f"- {example}" for example in command.examples],
        )
    )
    return "\n".join(lines).strip()


def build_unknown_command_guidance(
    command_name: str,
    *,
    available_commands: Sequence[str] | None = None,
) -> str:
    """Build guided help text for an unknown command."""

    if command_name in RENAMED_COMMANDS:
        replacement = RENAMED_COMMANDS[command_name]
        return build_command_guidance(
            replacement,
            reason=f"Command '{command_name}' was renamed to '{replacement}'.",
        )

    suggestions = suggest_command_names(
        command_name,
        available_commands=available_commands,
    )
    lines = [f"No such command '{command_name}'."]
    if suggestions:
        lines.extend(("", "Closest matches:"))
        for suggestion_name in suggestions:
            command = get_command_help(suggestion_name)
            if command is None:
                continue
            lines.append(f"- {command.usage}")
            lines.append(f"  {command.summary}")
    lines.extend(
        (
            "",
            "Use `researchbuddy --help` for the full command list.",
            "Use `researchbuddy commands` for the extended reference.",
        )
    )
    return "\n".join(lines).strip()


def _build_user_reference() -> str:
    lines = [
        "# ResearchBuddy CLI",
        "",
        "Primary entry points:",
        "- Installed command: `researchbuddy`",
        "- Local wrapper: `scripts/researchbuddy`",
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
        "# ResearchBuddy CLI For Agents",
        "",
        "Entrypoints:",
        "- `researchbuddy`",
        "- `scripts/researchbuddy`",
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
