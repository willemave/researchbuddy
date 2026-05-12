"""Validated models for skill installation."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

SkillInstallAgent = Literal["openclaw"]
SkillInstallScope = Literal["shared", "workspace"]
SkillInstallMethod = Literal["symlink", "copy"]
SkillInstallStatus = Literal["installed", "already_installed", "would_install", "blocked", "failed"]


class SkillInstallRequest(BaseModel):
    """Input for installing a bundled ResearchBuddy skill into an agent."""

    agent: SkillInstallAgent = "openclaw"
    scope: SkillInstallScope = "shared"
    method: SkillInstallMethod = "symlink"
    source_path: Path | None = None
    workspace_path: Path | None = None
    home_path: Path = Field(default_factory=Path.home)
    force: bool = False
    dry_run: bool = False


class SkillInstallResult(BaseModel):
    """Result of a skill install attempt."""

    ok: bool
    status: SkillInstallStatus
    agent: SkillInstallAgent
    skill_name: str
    scope: SkillInstallScope
    method: SkillInstallMethod
    source_path: Path | None
    target_path: Path
    detail: str
    next_steps: list[str] = Field(default_factory=list)
