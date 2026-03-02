import pytest
from pathlib import Path
from unittest.mock import MagicMock

from sdd_tui.core.models import PhaseState
from sdd_tui.core.pipeline import PipelineInferer, TaskParser


@pytest.fixture
def inferer() -> PipelineInferer:
    return PipelineInferer()


@pytest.fixture
def git_clean() -> MagicMock:
    mock = MagicMock()
    mock.is_clean.return_value = True
    return mock


@pytest.fixture
def git_dirty() -> MagicMock:
    mock = MagicMock()
    mock.is_clean.return_value = False
    return mock


# --- PipelineInferer ---

def test_all_pending_when_empty(change_dir: Path, inferer: PipelineInferer, git_clean: MagicMock) -> None:
    pipeline = inferer.infer(change_dir, git_clean)
    assert pipeline.propose == PhaseState.PENDING
    assert pipeline.spec == PhaseState.PENDING
    assert pipeline.design == PhaseState.PENDING
    assert pipeline.tasks == PhaseState.PENDING
    assert pipeline.apply == PhaseState.PENDING
    assert pipeline.verify == PhaseState.PENDING


def test_propose_done_when_proposal_exists(change_dir: Path, inferer: PipelineInferer, git_clean: MagicMock) -> None:
    (change_dir / "proposal.md").touch()
    pipeline = inferer.infer(change_dir, git_clean)
    assert pipeline.propose == PhaseState.DONE


def test_apply_done_when_all_tasks_checked(change_dir: Path, inferer: PipelineInferer, git_clean: MagicMock) -> None:
    (change_dir / "tasks.md").write_text("- [x] T01 Create something\n- [x] T02 Do another\n")
    pipeline = inferer.infer(change_dir, git_clean)
    assert pipeline.apply == PhaseState.DONE


def test_apply_pending_when_any_task_unchecked(change_dir: Path, inferer: PipelineInferer, git_clean: MagicMock) -> None:
    (change_dir / "tasks.md").write_text("- [x] T01 Create something\n- [ ] T02 Do another\n")
    pipeline = inferer.infer(change_dir, git_clean)
    assert pipeline.apply == PhaseState.PENDING


def test_verify_pending_when_apply_pending(change_dir: Path, inferer: PipelineInferer, git_clean: MagicMock) -> None:
    (change_dir / "tasks.md").write_text("- [ ] T01 Pending task\n")
    pipeline = inferer.infer(change_dir, git_clean)
    assert pipeline.verify == PhaseState.PENDING


def test_verify_done_when_apply_done_and_git_clean(change_dir: Path, inferer: PipelineInferer, git_clean: MagicMock) -> None:
    (change_dir / "tasks.md").write_text("- [x] T01 Done task\n")
    pipeline = inferer.infer(change_dir, git_clean)
    assert pipeline.verify == PhaseState.DONE


def test_verify_pending_when_git_dirty(change_dir: Path, inferer: PipelineInferer, git_dirty: MagicMock) -> None:
    (change_dir / "tasks.md").write_text("- [x] T01 Done task\n")
    pipeline = inferer.infer(change_dir, git_dirty)
    assert pipeline.verify == PhaseState.PENDING


# --- TaskParser ---

def test_parse_tasks_checked_and_unchecked(tmp_path: Path) -> None:
    tasks_md = tmp_path / "tasks.md"
    tasks_md.write_text("- [x] T01 Create Command\n- [ ] T02 Create Handler\n")
    tasks = TaskParser().parse(tasks_md)
    assert len(tasks) == 2
    assert tasks[0].id == "T01"
    assert tasks[0].done is True
    assert tasks[1].id == "T02"
    assert tasks[1].done is False


def test_parse_tasks_with_amendment(tmp_path: Path) -> None:
    tasks_md = tmp_path / "tasks.md"
    tasks_md.write_text(
        "- [x] T01 Create something\n"
        "── amendment: fix limit ──\n"
        "- [ ] T02 Fix validation\n"
    )
    tasks = TaskParser().parse(tasks_md)
    assert tasks[0].amendment is None
    assert tasks[1].amendment == "fix limit"


def test_parse_ignores_malformed_lines(tmp_path: Path) -> None:
    tasks_md = tmp_path / "tasks.md"
    tasks_md.write_text("- [x] Create something without TXX\n- [x] T01 Valid task\n")
    tasks = TaskParser().parse(tasks_md)
    assert len(tasks) == 1
    assert tasks[0].id == "T01"
