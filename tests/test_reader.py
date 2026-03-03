import pytest
from pathlib import Path

from sdd_tui.core.models import OpenspecNotFoundError
from sdd_tui.core.reader import OpenspecReader


@pytest.fixture
def reader() -> OpenspecReader:
    return OpenspecReader()


def test_missing_openspec_raises(tmp_path: Path, reader: OpenspecReader) -> None:
    with pytest.raises(OpenspecNotFoundError):
        reader.load(tmp_path / "openspec")


def test_empty_changes_returns_empty_list(openspec_dir: Path, reader: OpenspecReader) -> None:
    changes = reader.load(openspec_dir)
    assert changes == []


def test_lists_active_changes_alphabetically(openspec_dir: Path, reader: OpenspecReader) -> None:
    (openspec_dir / "changes" / "beta-change").mkdir()
    (openspec_dir / "changes" / "alpha-change").mkdir()
    (openspec_dir / "changes" / "archive" / "old-change").mkdir()

    changes = reader.load(openspec_dir)

    assert len(changes) == 2
    assert changes[0].name == "alpha-change"
    assert changes[1].name == "beta-change"


def test_archived_excluded_by_default(openspec_dir: Path, reader: OpenspecReader) -> None:
    (openspec_dir / "changes" / "active-change").mkdir()
    (openspec_dir / "changes" / "archive" / "2026-old-change").mkdir()

    changes = reader.load(openspec_dir)

    assert len(changes) == 1
    assert changes[0].name == "active-change"
    assert changes[0].archived is False


def test_include_archived_returns_all(openspec_dir: Path, reader: OpenspecReader) -> None:
    (openspec_dir / "changes" / "active-change").mkdir()
    (openspec_dir / "changes" / "archive" / "2026-old-change").mkdir()

    changes = reader.load(openspec_dir, include_archived=True)

    assert len(changes) == 2
    active = [c for c in changes if not c.archived]
    archived = [c for c in changes if c.archived]
    assert len(active) == 1
    assert active[0].name == "active-change"
    assert len(archived) == 1
    assert archived[0].name == "2026-old-change"


def test_include_archived_empty_archive(openspec_dir: Path, reader: OpenspecReader) -> None:
    (openspec_dir / "changes" / "active-change").mkdir()

    changes = reader.load(openspec_dir, include_archived=True)

    assert len(changes) == 1
    assert changes[0].archived is False
