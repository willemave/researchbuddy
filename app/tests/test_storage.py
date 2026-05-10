import asyncio
from datetime import UTC, datetime
from pathlib import Path

from app.models.review import RunRecord, RunRuntimeRecord
from app.services.storage import (
    create_run,
    fetch_current_run_id,
    fetch_run,
    fetch_run_runtime,
    finish_run_runtime,
    init_db,
    list_in_progress_runs,
    resolve_run_dir,
    set_current_run_id,
    upsert_run_runtime,
)


def test_fetch_run_returns_record(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    run_id = "run-123"
    created_at = datetime(2026, 1, 1, tzinfo=UTC)
    run = RunRecord(
        run_id=run_id,
        prompt="Test prompt",
        created_at=created_at,
        status="completed",
        max_urls=5,
        max_agents=2,
        headful=True,
        output_dir=tmp_path,
    )

    async def _run() -> None:
        await init_db(db_path)
        await create_run(db_path, run)
        fetched = await fetch_run(db_path, run_id)
        assert fetched is not None
        assert fetched.run_id == run_id
        assert fetched.prompt == run.prompt
        assert fetched.output_dir == tmp_path

    asyncio.run(_run())


def test_fetch_run_returns_none(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    async def _run() -> None:
        await init_db(db_path)
        fetched = await fetch_run(db_path, "missing")
        assert fetched is None

    asyncio.run(_run())


def test_resolve_run_dir_uses_stored_run_dir(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-123"
    assert resolve_run_dir(run_dir, "run-123") == run_dir


def test_resolve_run_dir_uses_override_base_dir(tmp_path: Path) -> None:
    override_dir = tmp_path / "storage"
    assert (
        resolve_run_dir(tmp_path / "old-run", "run-123", override_dir) == override_dir / "run-123"
    )


def test_resolve_run_dir_accepts_override_run_dir(tmp_path: Path) -> None:
    override_dir = tmp_path / "run-123"
    assert resolve_run_dir(tmp_path / "old-run", "run-123", override_dir) == override_dir


def test_current_run_and_runtime_round_trip(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    created_at = datetime(2026, 1, 1, tzinfo=UTC)
    started_at = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    run = RunRecord(
        run_id="run-123",
        prompt="Test prompt",
        created_at=created_at,
        status="in_progress",
        max_urls=5,
        max_agents=2,
        headful=True,
        output_dir=tmp_path / "run-123",
    )

    async def _run() -> None:
        await init_db(db_path)
        await create_run(db_path, run)
        await set_current_run_id(db_path, "run-123")
        await upsert_run_runtime(
            db_path,
            RunRuntimeRecord(
                run_id="run-123",
                pid=1234,
                log_path=tmp_path / "run-123" / "worker.log",
                started_at=started_at,
                updated_at=started_at,
            ),
        )

        assert await fetch_current_run_id(db_path) == "run-123"
        active_runs = await list_in_progress_runs(db_path)
        assert [item.run_id for item in active_runs] == ["run-123"]
        runtime = await fetch_run_runtime(db_path, "run-123")
        assert runtime is not None
        assert runtime.pid == 1234
        assert runtime.log_path == tmp_path / "run-123" / "worker.log"

        await finish_run_runtime(db_path, "run-123", exit_code=1)
        finished_runtime = await fetch_run_runtime(db_path, "run-123")
        assert finished_runtime is not None
        assert finished_runtime.exit_code == 1
        assert finished_runtime.finished_at is not None

    asyncio.run(_run())
