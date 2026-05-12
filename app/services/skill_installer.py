"""Install bundled ResearchBuddy skills into local agent runtimes."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path

from app.models.skills import SkillInstallRequest, SkillInstallResult

RESEARCH_SKILL_NAME = "research"
RESEARCHBUDDY_SKILL_DIR_ENV = "RESEARCHBUDDY_SKILL_DIR"


def install_skill(request: SkillInstallRequest) -> SkillInstallResult:
    """Install a bundled ResearchBuddy skill into a supported local agent.

    Args:
        request: Validated install request.

    Returns:
        Structured install result.
    """

    source_path = _resolve_skill_source(request.source_path)
    target_path = _resolve_target_path(request)
    next_steps = _build_next_steps(request.agent)

    if source_path is None:
        return SkillInstallResult(
            ok=False,
            status="failed",
            agent=request.agent,
            skill_name=RESEARCH_SKILL_NAME,
            scope=request.scope,
            method=request.method,
            source_path=None,
            target_path=target_path,
            detail=(
                "research skill source not found; pass --source or reinstall ResearchBuddy "
                "with the updated Homebrew formula"
            ),
            next_steps=[],
        )

    if not _is_valid_skill_dir(source_path):
        return SkillInstallResult(
            ok=False,
            status="failed",
            agent=request.agent,
            skill_name=RESEARCH_SKILL_NAME,
            scope=request.scope,
            method=request.method,
            source_path=source_path,
            target_path=target_path,
            detail=f"source path is not a skill directory with SKILL.md: {source_path}",
            next_steps=[],
        )

    existing_status = _classify_existing_target(target_path, source_path)
    if existing_status == "same":
        return SkillInstallResult(
            ok=True,
            status="already_installed",
            agent=request.agent,
            skill_name=RESEARCH_SKILL_NAME,
            scope=request.scope,
            method=request.method,
            source_path=source_path,
            target_path=target_path,
            detail="target already points at the ResearchBuddy skill",
            next_steps=next_steps,
        )

    if existing_status == "conflict" and not request.force:
        return SkillInstallResult(
            ok=False,
            status="blocked",
            agent=request.agent,
            skill_name=RESEARCH_SKILL_NAME,
            scope=request.scope,
            method=request.method,
            source_path=source_path,
            target_path=target_path,
            detail="target already exists; rerun with --force to replace it",
            next_steps=[],
        )

    if request.dry_run:
        action = "replace" if existing_status == "conflict" and request.force else "install"
        return SkillInstallResult(
            ok=True,
            status="would_install",
            agent=request.agent,
            skill_name=RESEARCH_SKILL_NAME,
            scope=request.scope,
            method=request.method,
            source_path=source_path,
            target_path=target_path,
            detail=f"would {action} {target_path}",
            next_steps=next_steps,
        )

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if existing_status == "conflict":
            _remove_target(target_path)
        if request.method == "symlink":
            target_path.symlink_to(source_path, target_is_directory=True)
        else:
            shutil.copytree(source_path, target_path)
    except OSError as exc:
        return SkillInstallResult(
            ok=False,
            status="failed",
            agent=request.agent,
            skill_name=RESEARCH_SKILL_NAME,
            scope=request.scope,
            method=request.method,
            source_path=source_path,
            target_path=target_path,
            detail=f"install failed: {exc}",
            next_steps=[],
        )

    return SkillInstallResult(
        ok=True,
        status="installed",
        agent=request.agent,
        skill_name=RESEARCH_SKILL_NAME,
        scope=request.scope,
        method=request.method,
        source_path=source_path,
        target_path=target_path,
        detail=f"installed {request.method} at {target_path}",
        next_steps=next_steps,
    )


def resolve_default_research_skill_dir(
    *,
    environ: Mapping[str, str] | None = None,
) -> Path | None:
    """Resolve the bundled research skill directory.

    Args:
        environ: Environment mapping used for tests or CLI process state.

    Returns:
        Skill directory path when found, otherwise ``None``.
    """

    env = environ or os.environ
    configured_path = env.get(RESEARCHBUDDY_SKILL_DIR_ENV, "").strip()
    candidates: list[Path] = []
    if configured_path:
        candidates.append(Path(configured_path).expanduser())

    repo_candidate = Path(__file__).resolve().parents[2] / "skills" / RESEARCH_SKILL_NAME
    candidates.append(repo_candidate)

    brew_prefix = _brew_formula_prefix()
    if brew_prefix is not None:
        candidates.append(brew_prefix / "share" / "researchbuddy" / "skills" / RESEARCH_SKILL_NAME)

    for candidate in candidates:
        if _is_valid_skill_dir(candidate):
            return candidate.resolve()
    return None


def _resolve_skill_source(source_path: Path | None) -> Path | None:
    if source_path is not None:
        return source_path.expanduser().resolve()
    return resolve_default_research_skill_dir()


def _resolve_target_path(request: SkillInstallRequest) -> Path:
    if request.scope == "shared":
        return request.home_path.expanduser() / ".openclaw" / "skills" / RESEARCH_SKILL_NAME

    workspace = request.workspace_path or Path.cwd()
    return workspace.expanduser().resolve() / "skills" / RESEARCH_SKILL_NAME


def _is_valid_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").is_file()


def _classify_existing_target(target_path: Path, source_path: Path) -> str:
    if not target_path.exists() and not target_path.is_symlink():
        return "missing"
    try:
        if target_path.resolve(strict=True) == source_path.resolve(strict=True):
            return "same"
    except OSError:
        return "conflict"
    if target_path.is_symlink():
        try:
            if target_path.resolve(strict=True) == source_path.resolve(strict=True):
                return "same"
        except OSError:
            return "conflict"
    return "conflict"


def _remove_target(target_path: Path) -> None:
    if target_path.is_symlink() or target_path.is_file():
        target_path.unlink()
        return
    shutil.rmtree(target_path)


def _build_next_steps(agent: str) -> list[str]:
    if agent == "openclaw":
        return [
            "start a new OpenClaw session or restart the gateway so the skill snapshot refreshes",
            "run `openclaw skills list --eligible` to verify the research skill is visible",
        ]
    return []


def _brew_formula_prefix() -> Path | None:
    brew_path = shutil.which("brew")
    if brew_path is None:
        return None
    try:
        completed = subprocess.run(
            [brew_path, "--prefix", "researchbuddy"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None

    prefix = completed.stdout.strip()
    if not prefix:
        return None
    return Path(prefix)
