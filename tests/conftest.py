import pytest
from pathlib import Path


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
