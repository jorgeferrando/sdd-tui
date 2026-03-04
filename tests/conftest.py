import pytest
from pathlib import Path
from unittest.mock import MagicMock

from sdd_tui.core.models import Change, Pipeline, PhaseState


@pytest.fixture
def openspec_dir(tmp_path: Path) -> Path:
    """Minimal openspec/ structure in a temporary directory."""
    openspec = tmp_path / "openspec"
    (openspec / "changes" / "archive").mkdir(parents=True)
    (openspec / "specs").mkdir()
    return openspec


@pytest.fixture
def change_dir(openspec_dir: Path) -> Path:
    """A single active change directory with no files."""
    change = openspec_dir / "changes" / "my-change"
    change.mkdir()
    return change


@pytest.fixture
def openspec_with_change(tmp_path: Path) -> Path:
    """openspec/ with 1 active change that has a tasks.md."""
    openspec = tmp_path / "openspec"
    (openspec / "changes" / "archive").mkdir(parents=True)
    (openspec / "specs").mkdir()
    change = openspec / "changes" / "my-change"
    change.mkdir()
    (change / "proposal.md").write_text("# Proposal\n")
    (change / "tasks.md").write_text("- [x] **T01** Done\n- [ ] **T02** Pending\n")
    return openspec


@pytest.fixture
def openspec_with_archive(openspec_with_change: Path) -> Path:
    """openspec/ with 1 active change and 1 archived change."""
    archived = openspec_with_change / "changes" / "archive" / "2026-01-01-old-change"
    archived.mkdir()
    (archived / "proposal.md").write_text("# Old Proposal\n")
    (archived / "tasks.md").write_text("- [x] **T01** Done\n")
    return openspec_with_change


@pytest.fixture
def mock_git() -> MagicMock:
    """GitReader mock that returns clean state and no commits."""
    m = MagicMock()
    m.is_clean.return_value = True
    m.find_commit.return_value = None
    return m


@pytest.fixture
def minimal_change(openspec_with_change: Path) -> Change:
    """A minimal Change object for screens that require one."""
    change_path = openspec_with_change / "changes" / "my-change"
    pipeline = Pipeline(
        propose=PhaseState.DONE,
        spec=PhaseState.PENDING,
        design=PhaseState.PENDING,
        tasks=PhaseState.DONE,
        apply=PhaseState.PENDING,
        verify=PhaseState.PENDING,
    )
    return Change(name="my-change", path=change_path, pipeline=pipeline)
