from pathlib import Path

import pytest

from sdd_tui.core.config import AppConfig, ProjectConfig
from sdd_tui.core.models import OpenspecNotFoundError
from sdd_tui.core.reader import OpenspecReader, load_all_changes, load_spec_json, load_steering


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


# --- load_steering ---


def test_load_steering_exists(tmp_path: Path) -> None:
    openspec_path = tmp_path / "openspec"
    openspec_path.mkdir()
    (openspec_path / "steering.md").write_text("# Project\n\nSome context.")

    result = load_steering(openspec_path)

    assert result == "# Project\n\nSome context."


def test_load_steering_missing(tmp_path: Path) -> None:
    openspec_path = tmp_path / "openspec"
    openspec_path.mkdir()

    result = load_steering(openspec_path)

    assert result is None


def test_load_steering_empty_file(tmp_path: Path) -> None:
    openspec_path = tmp_path / "openspec"
    openspec_path.mkdir()
    (openspec_path / "steering.md").write_text("")

    result = load_steering(openspec_path)

    assert result == ""


# --- load_spec_json ---


def test_load_spec_json_valid(tmp_path: Path) -> None:
    change_path = tmp_path / "my-change"
    change_path.mkdir()
    (change_path / "spec.json").write_text('{"change": "my-change", "version": "1.0"}')

    result = load_spec_json(change_path)

    assert result == {"change": "my-change", "version": "1.0"}


def test_load_spec_json_missing(tmp_path: Path) -> None:
    change_path = tmp_path / "my-change"
    change_path.mkdir()

    result = load_spec_json(change_path)

    assert result is None


def test_load_spec_json_malformed(tmp_path: Path) -> None:
    change_path = tmp_path / "my-change"
    change_path.mkdir()
    (change_path / "spec.json").write_text("{not valid json")

    result = load_spec_json(change_path)

    assert result is None


# --- project fields ---


def test_load_sets_project_fields(openspec_dir: Path, reader: OpenspecReader) -> None:
    (openspec_dir / "changes" / "my-change").mkdir()
    project_root = openspec_dir.parent

    changes = reader.load(openspec_dir, project_path=project_root)

    assert len(changes) == 1
    assert changes[0].project == project_root.name
    assert changes[0].project_path == project_root


def test_load_default_project_path_is_parent(openspec_dir: Path, reader: OpenspecReader) -> None:
    (openspec_dir / "changes" / "my-change").mkdir()

    changes = reader.load(openspec_dir)

    assert changes[0].project_path == openspec_dir.parent


def test_load_archived_has_project_fields(openspec_dir: Path, reader: OpenspecReader) -> None:
    (openspec_dir / "changes" / "archive" / "old-change").mkdir()
    project_root = openspec_dir.parent

    changes = reader.load(openspec_dir, include_archived=True, project_path=project_root)

    archived = [c for c in changes if c.archived]
    assert len(archived) == 1
    assert archived[0].project == project_root.name
    assert archived[0].project_path == project_root


# --- load_all_changes ---


def _make_project(base: Path, name: str) -> Path:
    """Create a minimal openspec structure under base/name/."""
    proj = base / name
    (proj / "openspec" / "changes").mkdir(parents=True)
    (proj / "openspec" / "changes" / "archive").mkdir()
    return proj


def test_load_all_changes_legacy_uses_cwd(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, "myproject")
    (proj / "openspec" / "changes" / "my-change").mkdir()

    changes = load_all_changes(AppConfig(), proj)

    assert len(changes) == 1
    assert changes[0].project == "myproject"
    assert changes[0].project_path == proj


def test_load_all_changes_multi_project(tmp_path: Path) -> None:
    proj_a = _make_project(tmp_path, "alpha")
    proj_b = _make_project(tmp_path, "beta")
    (proj_a / "openspec" / "changes" / "change-a").mkdir()
    (proj_b / "openspec" / "changes" / "change-b").mkdir()

    config = AppConfig(projects=[ProjectConfig(path=proj_a), ProjectConfig(path=proj_b)])
    changes = load_all_changes(config, tmp_path)

    assert len(changes) == 2
    names = {c.name for c in changes}
    assert names == {"change-a", "change-b"}
    projects = {c.project for c in changes}
    assert projects == {"alpha", "beta"}


def test_load_all_changes_skips_missing_project(tmp_path: Path) -> None:
    proj_a = _make_project(tmp_path, "alpha")
    (proj_a / "openspec" / "changes" / "change-a").mkdir()
    missing = tmp_path / "ghost"  # does not exist

    config = AppConfig(projects=[ProjectConfig(path=proj_a), ProjectConfig(path=missing)])
    changes = load_all_changes(config, tmp_path)

    assert len(changes) == 1
    assert changes[0].name == "change-a"


def test_load_all_changes_all_missing_returns_empty(tmp_path: Path) -> None:
    config = AppConfig(projects=[ProjectConfig(path=tmp_path / "ghost")])
    changes = load_all_changes(config, tmp_path)
    assert changes == []
