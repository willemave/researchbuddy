from datetime import UTC, datetime

from typer.testing import CliRunner

from app import cli
from app.cli_doctor import DoctorCheck
from app.cli_help import build_command_reference
from app.models.review import RunRecord
from app.services.setup_runtime import SetupAction, SetupResult

runner = CliRunner()


def test_build_command_reference_includes_primary_commands() -> None:
    reference = build_command_reference()

    assert 'reviewbuddy run "<prompt>" [--result-file answer.md] [--stats]' in reference
    assert "reviewbuddy ask" in reference
    assert "reviewbuddy runs [--limit 20]" in reference
    assert "reviewbuddy setup" in reference
    assert "reviewbuddy doctor" in reference
    assert "reviewbuddy tap export" in reference
    assert "docs/agent-cli-reference.md" in reference
    assert "Prints a full readiness report and exits non-zero when setup or runtime checks fail." in reference
    assert "Prints the run ID and final synthesis to stdout" in reference


def test_build_command_reference_agent_mode_is_machine_friendly() -> None:
    reference = build_command_reference(agent=True)

    assert "## ask" in reference
    assert "Purpose:" in reference
    assert 'Usage: `reviewbuddy ask <run_id> "<question>" [--result-file answer.txt]`' in reference
    assert "Returns enough detail to drive scripts or agents without opening the docs first." in reference


def test_commands_command_prints_agent_reference() -> None:
    result = runner.invoke(cli.app, ["commands", "--agent"])

    assert result.exit_code == 0
    assert "ReviewBuddy CLI For Agents" in result.stdout
    assert 'Usage: `reviewbuddy ask <run_id> "<question>" [--result-file answer.txt]`' in result.stdout
    assert "## setup" in result.stdout
    assert "## tap export" in result.stdout


def test_top_level_help_uses_descriptive_command_text() -> None:
    result = runner.invoke(cli.app, ["--help"])

    assert result.exit_code == 0
    assert "Run ReviewBuddy research workflows, inspect saved runs, and validate local" in result.stdout
    assert "runtime readiness." in result.stdout
    assert "Run a new research workflow and print the final synthesis" in result.stdout
    assert "Print usage, behavior, and examples for every CLI command." in result.stdout
    assert "List recent saved runs with their run IDs, timestamps, status," in result.stdout
    assert "and prompt summaries." in result.stdout


def test_runs_command_lists_recent_runs(monkeypatch) -> None:
    async def fake_list_runs(_db_path, limit=20):  # noqa: ANN001, ANN202
        assert limit == 5
        return [
            RunRecord(
                run_id="run-123",
                prompt="Best office chair for long coding sessions with strong lumbar support",
                created_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
                status="completed",
                max_urls=10,
                max_agents=4,
                headful=True,
                output_dir=cli.Path("/tmp/run-123"),
            )
        ]

    monkeypatch.setattr(cli, "list_runs", fake_list_runs)

    result = runner.invoke(cli.app, ["runs", "--limit", "5"])

    assert result.exit_code == 0
    assert "# Recent Runs" in result.stdout
    assert "run-123" in result.stdout
    assert "completed" in result.stdout
    assert "Best office chair for long coding sessions" in result.stdout


def test_runs_command_handles_empty_history(monkeypatch) -> None:
    async def fake_list_runs(_db_path, limit=20):  # noqa: ANN001, ANN202
        del limit
        return []

    monkeypatch.setattr(cli, "list_runs", fake_list_runs)

    result = runner.invoke(cli.app, ["runs"])

    assert result.exit_code == 0
    assert "No runs found." in result.stdout


def test_interactive_commands_are_not_registered() -> None:
    interactive_result = runner.invoke(cli.app, ["interactive"])
    resume_result = runner.invoke(cli.app, ["resume", "abc123"])

    assert interactive_result.exit_code == 2
    assert resume_result.exit_code == 2


def test_doctor_command_returns_nonzero_on_failures(monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "run_doctor_checks",
        lambda _settings: [DoctorCheck(name="local agent harness", ok=False, detail="missing")],
    )

    result = runner.invoke(cli.app, ["doctor"])

    assert result.exit_code == 1
    assert "[FAIL] local agent harness" in result.stdout


def test_doctor_command_fix_runs_setup_and_reports_results(monkeypatch) -> None:
    captured: dict[str, bool] = {}

    def fake_run_setup(_settings, install_playwright):  # noqa: ANN001, ANN202
        captured["install_playwright"] = install_playwright
        return SetupResult(
            actions=[SetupAction(name="playwright browsers", ok=True, detail="installed")],
            doctor_checks=[DoctorCheck(name="playwright browsers", ok=True, detail="Chromium launch OK")],
        )

    monkeypatch.setattr(cli, "run_setup", fake_run_setup)

    result = runner.invoke(cli.app, ["doctor", "--fix", "--skip-playwright"])

    assert result.exit_code == 0
    assert captured["install_playwright"] is False
    assert "ReviewBuddy Setup" in result.stdout
    assert "ReviewBuddy Doctor" in result.stdout
    assert "[OK] playwright browsers" in result.stdout


def test_doctor_command_fix_returns_nonzero_on_setup_failures(monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "run_setup",
        lambda _settings, install_playwright: SetupResult(
            actions=[SetupAction(name="playwright browsers", ok=False, detail="install failed")],
            doctor_checks=[DoctorCheck(name="playwright browsers", ok=True, detail="Chromium launch OK")],
        ),
    )

    result = runner.invoke(cli.app, ["doctor", "--fix"])

    assert result.exit_code == 1
    assert "[FAIL] playwright browsers: install failed" in result.stdout


def test_setup_command_prints_setup_and_doctor_reports(monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "run_setup",
        lambda _settings, install_playwright: SetupResult(
            actions=[SetupAction(name="search config", ok=True, detail="configured")],
            doctor_checks=[DoctorCheck(name="local agent harness", ok=True, detail="codex")],
        ),
    )

    result = runner.invoke(cli.app, ["setup", "--skip-playwright"])

    assert result.exit_code == 0
    assert "ReviewBuddy Setup" in result.stdout
    assert "ReviewBuddy Doctor" in result.stdout
    assert "[OK] search config" in result.stdout


def test_run_command_only_prints_stats_when_requested(monkeypatch) -> None:
    monkeypatch.setattr(cli, "setup_logging", lambda _level: None)

    async def fake_run_review(_request, _deps, reporter=None):  # noqa: ANN001, ANN202
        assert reporter is not None
        reporter.on_lanes_planned(2)
        reporter.on_urls_discovered(3)
        reporter.on_url_done(True)
        return cli.ReviewRunResult(
            run_id="run-123",
            prompt="Best office chair",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            stats=cli.ReviewRunStats(total_urls=4, fetched=3, failed=1),
            synthesis_markdown="Saved synthesis text",
        )

    monkeypatch.setattr(
        cli,
        "run_review",
        fake_run_review,
    )

    default_result = runner.invoke(cli.app, ["run", "Best office chair"])
    stats_result = runner.invoke(cli.app, ["run", "Best office chair", "--stats"])

    assert default_result.exit_code == 0
    assert 'Starting ReviewBuddy run for: "Best office chair"' in default_result.stdout
    assert "Planned 2 lanes. Starting crawl." in default_result.stdout
    assert "Queued 3 URLs for fetch." in default_result.stdout
    assert "Processed 1 URLs (1 fetched, 0 failed)." in default_result.stdout
    assert "Run ID: run-123" in default_result.stdout
    assert "Fetched 3/4 URLs" not in default_result.stdout
    assert "Saved synthesis text" in default_result.stdout

    assert stats_result.exit_code == 0
    assert "Fetched 3/4 URLs (1 failed)" in stats_result.stdout


def test_run_command_accepts_prompt_file_and_result_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(cli, "setup_logging", lambda _level: None)
    prompt_path = tmp_path / "prompt.txt"
    result_path = tmp_path / "outputs" / "synthesis.md"
    prompt_path.write_text("Best office chair", encoding="utf-8")
    captured: dict[str, str] = {}

    async def fake_run_review(request, _deps, reporter=None):  # noqa: ANN001, ANN202
        del reporter
        captured["prompt"] = request.prompt
        return cli.ReviewRunResult(
            run_id="run-123",
            prompt=request.prompt,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            stats=cli.ReviewRunStats(total_urls=4, fetched=3, failed=1),
            synthesis_markdown="Saved synthesis text",
        )

    monkeypatch.setattr(cli, "run_review", fake_run_review)

    result = runner.invoke(
        cli.app,
        [
            "run",
            "--prompt-file",
            str(prompt_path),
            "--result-file",
            str(result_path),
        ],
    )

    assert result.exit_code == 0
    assert captured["prompt"] == "Best office chair"
    assert result_path.read_text(encoding="utf-8") == "Saved synthesis text"
    assert 'Starting ReviewBuddy run for: "Best office chair"' in result.output
    assert f"Result file: {result_path}" in result.output


def test_ask_command_prints_startup_status(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(cli, "setup_logging", lambda _level: None)

    async def fake_load_state(run_id, output_dir=None):  # noqa: ANN001, ANN202
        del output_dir
        report = cli.ReviewRunResult(
            run_id=run_id,
            prompt="Best office chair",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            stats=cli.ReviewRunStats(total_urls=4, fetched=3, failed=1),
            synthesis_markdown="Saved synthesis text",
        )
        state = cli.FollowupSessionState(
            run_id=run_id,
            run_dir=tmp_path,
            prompt=report.prompt,
            synthesis_markdown=report.synthesis_markdown,
        )
        return report, state

    async def fake_ensure_memory(state):  # noqa: ANN001, ANN202
        return cli.FollowupMemory(
            run_id=state.run_id,
            prompt=state.prompt,
            synthesis_markdown=state.synthesis_markdown,
            source_cards=[],
        )

    async def fake_answer(memory, question, model_name=None):  # noqa: ANN001, ANN202
        del memory, model_name
        assert question == "What broke most often?"
        return "Answer text"

    monkeypatch.setattr(cli, "_load_followup_state_for_run", fake_load_state)
    monkeypatch.setattr(cli, "_ensure_followup_memory", fake_ensure_memory)
    monkeypatch.setattr(cli, "answer_followup_question", fake_answer)

    result = runner.invoke(cli.app, ["ask", "run-123", "What broke most often?"])

    assert result.exit_code == 0
    assert "Loading saved run run-123 for follow-up." in result.stdout
    assert 'Running follow-up answer for: "What broke most often?"' in result.stdout
    assert "Answer text" in result.stdout


def test_run_command_rejects_argument_and_prompt_file(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(cli, "setup_logging", lambda _level: None)
    prompt_path = tmp_path / "prompt.txt"
    prompt_path.write_text("Best office chair", encoding="utf-8")

    result = runner.invoke(
        cli.app,
        ["run", "Best office chair", "--prompt-file", str(prompt_path)],
    )

    assert result.exit_code == 2
    assert "Pass either the prompt argument or --prompt-file, not both." in result.output


def test_tap_export_command_writes_tap_repo(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        cli, "detect_github_remote", lambda _repo_root: ("willemave", "reviewbuddy")
    )

    output_dir = tmp_path / "homebrew-reviewbuddy"
    result = runner.invoke(cli.app, ["tap", "export", "--output-dir", str(output_dir)])

    assert result.exit_code == 0
    assert (output_dir / "Formula" / "reviewbuddy.rb").exists()
    assert (output_dir / "skills" / "reviewbuddy-tap-maintainer" / "SKILL.md").exists()
