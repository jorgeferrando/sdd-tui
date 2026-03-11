"""Tests for scripts/changelog.py — importable as a module."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

# Make scripts/ importable
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from changelog import (  # noqa: E402
    ChangeEntry,
    VersionBoundary,
    assign_changes_to_versions,
    collect_archived_changes,
    collect_version_boundaries,
    extract_section,
    mark_version,
    render_changelog,
)


# ---------------------------------------------------------------------------
# collect_archived_changes
# ---------------------------------------------------------------------------


def test_collect_archived_changes_empty_dir(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()
    assert collect_archived_changes(archive) == []


def test_collect_archived_changes_missing_dir(tmp_path: Path) -> None:
    assert collect_archived_changes(tmp_path / "nonexistent") == []


def test_collect_archived_changes_reads_description(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    change_dir = archive / "2026-03-11-my-feature"
    change_dir.mkdir(parents=True)
    (change_dir / "proposal.md").write_text(
        "# Proposal\n\n## Descripción\n\nAdd a great new feature to the TUI.\n"
    )
    entries = collect_archived_changes(archive)
    assert len(entries) == 1
    assert entries[0].name == "my-feature"
    assert entries[0].date == date(2026, 3, 11)
    assert "great new feature" in entries[0].description


def test_collect_archived_changes_nested_proposal(tmp_path: Path) -> None:
    """Some archives have change_dir/{change_name}/proposal.md."""
    archive = tmp_path / "archive"
    change_dir = archive / "2026-03-05-pr-status"
    nested = change_dir / "pr-status"
    nested.mkdir(parents=True)
    (nested / "proposal.md").write_text(
        "# Proposal\n\n## Descripción\n\nShow PR status in pipeline.\n"
    )
    entries = collect_archived_changes(archive)
    assert len(entries) == 1
    assert "PR status" in entries[0].description


def test_collect_archived_changes_fallback_description(tmp_path: Path) -> None:
    """Falls back to first non-empty line if ## Descripción section absent."""
    archive = tmp_path / "archive"
    change_dir = archive / "2026-03-02-bootstrap"
    change_dir.mkdir(parents=True)
    (change_dir / "proposal.md").write_text("# Proposal\n\nInitial skeleton.\n")
    entries = collect_archived_changes(archive)
    assert entries[0].description == "Initial skeleton."


def test_collect_archived_changes_skips_non_dir(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "README.md").write_text("notes")
    (archive / "2026-03-01-real-change").mkdir()
    (archive / "2026-03-01-real-change" / "proposal.md").write_text(
        "# P\n\n## Descripción\n\nSomething.\n"
    )
    entries = collect_archived_changes(archive)
    assert len(entries) == 1


def test_collect_archived_changes_sorted_by_date(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    for name in ["2026-03-03-c", "2026-03-01-a", "2026-03-02-b"]:
        d = archive / name
        d.mkdir(parents=True)
        (d / "proposal.md").write_text(f"# P\n\n## Descripción\n\n{name}.\n")
    entries = collect_archived_changes(archive)
    # collect_archived_changes returns sorted by directory name (alphabetical)
    assert [e.name for e in entries] == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# collect_version_boundaries — markers
# ---------------------------------------------------------------------------


def _make_marker(versions_dir: Path, version: str, date_str: str) -> None:
    versions_dir.mkdir(parents=True, exist_ok=True)
    (versions_dir / f"{version}.yaml").write_text(f"date: {date_str}\n")


def test_collect_version_boundaries_from_markers(tmp_path: Path) -> None:
    versions_dir = tmp_path / "openspec" / "versions"
    _make_marker(versions_dir, "0.2.0", "2026-03-11")
    _make_marker(versions_dir, "0.1.0", "2026-03-01")

    # Patch find_repo_root equivalent: pass root directly
    # We call _boundaries_from_markers indirectly via collect_version_boundaries
    # with release_enabled=False (uses markers only)
    import changelog as cl

    orig = cl.find_repo_root
    cl.find_repo_root = lambda: tmp_path  # type: ignore[assignment]
    try:
        boundaries = collect_version_boundaries(tmp_path, release_enabled=False)
    finally:
        cl.find_repo_root = orig

    assert len(boundaries) == 2
    versions = {b.version for b in boundaries}
    assert versions == {"0.2.0", "0.1.0"}
    assert all(b.source == "marker" for b in boundaries)


def test_collect_version_boundaries_no_markers_no_tags(tmp_path: Path) -> None:
    import changelog as cl

    orig = cl.find_repo_root
    cl.find_repo_root = lambda: tmp_path  # type: ignore[assignment]
    try:
        boundaries = collect_version_boundaries(tmp_path, release_enabled=False)
    finally:
        cl.find_repo_root = orig

    assert boundaries == []


# ---------------------------------------------------------------------------
# assign_changes_to_versions
# ---------------------------------------------------------------------------


def test_assign_all_to_unreleased_when_no_boundaries() -> None:
    changes = [
        ChangeEntry("a", date(2026, 3, 1), "desc a"),
        ChangeEntry("b", date(2026, 3, 5), "desc b"),
    ]
    result = assign_changes_to_versions(changes, [])
    assert "[Unreleased]" in result
    assert len(result["[Unreleased]"]) == 2


def test_assign_changes_by_boundary_date() -> None:
    changes = [
        ChangeEntry("old", date(2026, 3, 1), "old change"),
        ChangeEntry("new", date(2026, 3, 11), "new change"),
        ChangeEntry("future", date(2026, 3, 15), "future change"),
    ]
    boundaries = [
        VersionBoundary("0.2.0", date(2026, 3, 11), "marker"),
        VersionBoundary("0.1.0", date(2026, 3, 5), "marker"),
    ]
    result = assign_changes_to_versions(changes, boundaries)

    assert "old" in [e.name for e in result.get("0.1.0", [])]
    assert "new" in [e.name for e in result.get("0.2.0", [])]
    assert "future" in [e.name for e in result.get("[Unreleased]", [])]


def test_change_on_boundary_date_belongs_to_that_version() -> None:
    changes = [ChangeEntry("exact", date(2026, 3, 11), "exact date match")]
    boundaries = [VersionBoundary("0.2.0", date(2026, 3, 11), "marker")]
    result = assign_changes_to_versions(changes, boundaries)
    assert "exact" in [e.name for e in result.get("0.2.0", [])]
    assert "[Unreleased]" not in result


# ---------------------------------------------------------------------------
# render_changelog
# ---------------------------------------------------------------------------


def test_render_changelog_unreleased_only() -> None:
    assignments = {"[Unreleased]": [ChangeEntry("feat", date(2026, 3, 11), "A feature")]}
    output = render_changelog(assignments, [], "https://github.com/user/repo")
    assert "## [Unreleased]" in output
    assert "`feat`: A feature" in output


def test_render_changelog_versioned_section() -> None:
    assignments = {
        "0.2.0": [ChangeEntry("my-feature", date(2026, 3, 11), "Great thing")],
    }
    boundaries = [VersionBoundary("0.2.0", date(2026, 3, 11), "marker")]
    output = render_changelog(assignments, boundaries, "")
    assert "## [0.2.0] — 2026-03-11" in output
    assert "`my-feature`: Great thing" in output


def test_render_changelog_includes_reference_links() -> None:
    assignments = {"0.2.0": [ChangeEntry("f", date(2026, 3, 11), "d")]}
    boundaries = [VersionBoundary("0.2.0", date(2026, 3, 11), "marker")]
    output = render_changelog(assignments, boundaries, "https://github.com/u/r")
    assert "[0.2.0]: https://github.com/u/r/releases/tag/v0.2.0" in output


# ---------------------------------------------------------------------------
# extract_section
# ---------------------------------------------------------------------------


def test_extract_section_returns_correct_block() -> None:
    changelog = (
        "# Changelog\n\n"
        "## [0.3.0] — 2026-04-01\n\n"
        "- `new`: something\n\n"
        "## [0.2.0] — 2026-03-11\n\n"
        "- `old`: old thing\n\n"
        "[0.2.0]: https://...\n"
    )
    section = extract_section(changelog, "0.2.0")
    assert "old thing" in section
    assert "something" not in section


def test_extract_section_returns_empty_for_unknown_version() -> None:
    changelog = "# Changelog\n\n## [0.1.0] — 2026-01-01\n\n- `x`: y\n"
    assert extract_section(changelog, "9.9.9") == ""


# ---------------------------------------------------------------------------
# mark_version
# ---------------------------------------------------------------------------


def test_mark_version_creates_yaml_file(tmp_path: Path) -> None:
    marker = mark_version(tmp_path, "0.2.0")
    assert marker.exists()
    assert marker.name == "0.2.0.yaml"
    content = marker.read_text()
    assert "date:" in content


def test_mark_version_creates_versions_dir_if_missing(tmp_path: Path) -> None:
    # tmp_path has no openspec/versions/ yet
    root = tmp_path / "repo"
    root.mkdir()
    marker = mark_version(root, "1.0.0")
    assert (root / "openspec" / "versions" / "1.0.0.yaml").exists()


def test_mark_version_date_is_today(tmp_path: Path) -> None:
    marker = mark_version(tmp_path, "0.3.0")
    today = date.today().isoformat()
    assert today in marker.read_text()
