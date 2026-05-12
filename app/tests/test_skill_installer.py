from pathlib import Path

from app.models.skills import SkillInstallRequest
from app.services.skill_installer import install_skill, resolve_default_research_skill_dir


def write_skill(path: Path) -> Path:
    skill_path = path / "research"
    skill_path.mkdir(parents=True)
    (skill_path / "SKILL.md").write_text(
        "---\nname: research\ndescription: Test skill.\n---\n",
        encoding="utf-8",
    )
    return skill_path


def test_install_skill_symlinks_shared_openclaw_skill(tmp_path: Path) -> None:
    source_path = write_skill(tmp_path / "source")

    result = install_skill(
        SkillInstallRequest(
            source_path=source_path,
            home_path=tmp_path / "home",
        )
    )

    assert result.ok is True
    assert result.status == "installed"
    assert result.target_path == tmp_path / "home" / ".openclaw" / "skills" / "research"
    assert result.target_path.is_symlink()
    assert result.target_path.resolve() == source_path
    assert "openclaw skills list --eligible" in result.next_steps[1]


def test_install_skill_is_idempotent_when_target_points_to_source(tmp_path: Path) -> None:
    source_path = write_skill(tmp_path / "source")
    request = SkillInstallRequest(
        source_path=source_path,
        home_path=tmp_path / "home",
    )

    first_result = install_skill(request)
    second_result = install_skill(request)

    assert first_result.status == "installed"
    assert second_result.ok is True
    assert second_result.status == "already_installed"


def test_install_skill_blocks_existing_target_without_force(tmp_path: Path) -> None:
    source_path = write_skill(tmp_path / "source")
    target_path = tmp_path / "home" / ".openclaw" / "skills" / "research"
    target_path.mkdir(parents=True)
    (target_path / "SKILL.md").write_text(
        "---\nname: research\ndescription: Existing skill.\n---\n",
        encoding="utf-8",
    )

    result = install_skill(
        SkillInstallRequest(
            source_path=source_path,
            home_path=tmp_path / "home",
        )
    )

    assert result.ok is False
    assert result.status == "blocked"
    assert "rerun with --force" in result.detail


def test_install_skill_dry_run_reports_replacement_without_writing(tmp_path: Path) -> None:
    source_path = write_skill(tmp_path / "source")
    target_path = tmp_path / "home" / ".openclaw" / "skills" / "research"
    target_path.mkdir(parents=True)
    (target_path / "SKILL.md").write_text(
        "---\nname: research\ndescription: Existing skill.\n---\n",
        encoding="utf-8",
    )

    result = install_skill(
        SkillInstallRequest(
            source_path=source_path,
            home_path=tmp_path / "home",
            force=True,
            dry_run=True,
        )
    )

    assert result.ok is True
    assert result.status == "would_install"
    assert target_path.is_dir()
    assert not target_path.is_symlink()


def test_install_skill_copies_to_workspace_scope(tmp_path: Path) -> None:
    source_path = write_skill(tmp_path / "source")
    workspace_path = tmp_path / "workspace"

    result = install_skill(
        SkillInstallRequest(
            source_path=source_path,
            scope="workspace",
            method="copy",
            workspace_path=workspace_path,
            home_path=tmp_path / "home",
        )
    )

    assert result.ok is True
    assert result.target_path == workspace_path / "skills" / "research"
    assert not result.target_path.is_symlink()
    assert (result.target_path / "SKILL.md").is_file()


def test_resolve_default_research_skill_dir_reads_env(tmp_path: Path) -> None:
    source_path = write_skill(tmp_path / "source")

    result = resolve_default_research_skill_dir(
        environ={"RESEARCHBUDDY_SKILL_DIR": str(source_path)}
    )

    assert result == source_path.resolve()
