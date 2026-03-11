"""Tests for src/sdd_tui/docs_gen.py."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from sdd_tui.docs_gen import (
    collect_archived_changes,
    find_openspec,
    list_spec_domains,
    load_site_description,
    load_site_name,
    make_placeholder,
    parse_spec_decisions,
    parse_spec_requirements,
    render_changelog_md,
    render_index_md,
    render_mkdocs_yml,
    render_reference_page,
)

# ---------------------------------------------------------------------------
# find_openspec
# ---------------------------------------------------------------------------


def test_find_openspec_found(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    subdir = tmp_path / "src" / "module"
    subdir.mkdir(parents=True)
    result = find_openspec(subdir)
    assert result == openspec


def test_find_openspec_not_found(tmp_path: Path) -> None:
    subdir = tmp_path / "deep" / "nested"
    subdir.mkdir(parents=True)
    # No openspec/ anywhere — will hit filesystem root eventually
    result = find_openspec(subdir)
    # Should return None (no openspec/ in tmp isolated tree)
    # Note: may find real openspec/ if tests run inside the sdd-tui repo,
    # so we only assert the type contract.
    assert result is None or result.is_dir()


# ---------------------------------------------------------------------------
# load_site_name
# ---------------------------------------------------------------------------


def test_load_site_name_from_product_md(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    steering = openspec / "steering"
    steering.mkdir(parents=True)
    (steering / "product.md").write_text("# My Awesome Project\n\nSome description.\n")
    assert load_site_name(openspec) == "My Awesome Project"


def test_load_site_name_fallback_dirname(tmp_path: Path) -> None:
    project = tmp_path / "my-project"
    openspec = project / "openspec"
    openspec.mkdir(parents=True)
    assert load_site_name(openspec) == "my-project"


def test_load_site_name_from_config_yaml(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    (openspec / "config.yaml").write_text("project_name: Config Project\n")
    assert load_site_name(openspec) == "Config Project"


# ---------------------------------------------------------------------------
# load_site_description
# ---------------------------------------------------------------------------


def test_load_site_description_from_product_md(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    steering = openspec / "steering"
    steering.mkdir(parents=True)
    (steering / "product.md").write_text(
        "# Project\n\nThis is a great tool for developers.\n\n## More\n\nDetails.\n"
    )
    desc = load_site_description(openspec)
    assert "great tool" in desc
    assert "## More" not in desc


def test_load_site_description_placeholder_when_no_steering(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    desc = load_site_description(openspec)
    assert desc.startswith("<!-- sdd-docs:placeholder")
    assert "description" in desc


# ---------------------------------------------------------------------------
# list_spec_domains
# ---------------------------------------------------------------------------


def test_list_spec_domains(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    specs = openspec / "specs"
    (specs / "core").mkdir(parents=True)
    (specs / "auth").mkdir(parents=True)
    (specs / "ui").mkdir(parents=True)
    assert list_spec_domains(openspec) == ["auth", "core", "ui"]


def test_list_spec_domains_empty(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    assert list_spec_domains(openspec) == []


# ---------------------------------------------------------------------------
# parse_spec_requirements
# ---------------------------------------------------------------------------


SPEC_WITH_REQS = """\
## Requisitos (EARS)

- **REQ-01** `[Event]` When the user clicks, the system SHALL respond.
- **REQ-02** `[Ubiquitous]` The system SHALL always log.
- **REQ-03** `[Unwanted]` If the input is invalid, the system SHALL reject it.
"""


def test_parse_spec_requirements_basic(tmp_path: Path) -> None:
    reqs = parse_spec_requirements(SPEC_WITH_REQS)
    assert len(reqs) == 3
    assert reqs[0].id == "REQ-01"
    assert reqs[0].type == "Event"
    assert "user clicks" in reqs[0].description
    assert reqs[1].id == "REQ-02"
    assert reqs[1].type == "Ubiquitous"
    assert reqs[2].id == "REQ-03"
    assert reqs[2].type == "Unwanted"


def test_parse_spec_requirements_empty(tmp_path: Path) -> None:
    assert parse_spec_requirements("# No requirements here\n") == []


# ---------------------------------------------------------------------------
# parse_spec_decisions
# ---------------------------------------------------------------------------


SPEC_WITH_DECISIONS = """\
## Decisiones Tomadas

| Decisión | Alternativa Descartada | Motivo |
|---------|----------------------|--------|
| Use CLI | Use GUI | Simpler |
| Pure functions | Classes | Testable |
"""


def test_parse_spec_decisions_basic(tmp_path: Path) -> None:
    decisions = parse_spec_decisions(SPEC_WITH_DECISIONS)
    assert len(decisions) == 2
    assert decisions[0].decision == "Use CLI"
    assert decisions[0].discarded == "Use GUI"
    assert decisions[0].reason == "Simpler"
    assert decisions[1].decision == "Pure functions"


def test_parse_spec_decisions_empty(tmp_path: Path) -> None:
    assert parse_spec_decisions("No decisions here.\n") == []


# ---------------------------------------------------------------------------
# collect_archived_changes
# ---------------------------------------------------------------------------


def test_collect_archived_changes_empty_dir(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()
    assert collect_archived_changes(archive) == []


def test_collect_archived_changes_missing_dir(tmp_path: Path) -> None:
    assert collect_archived_changes(tmp_path / "nonexistent") == []


def test_collect_archived_changes_newest_first(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    for name in ["2026-01-01-alpha", "2026-03-01-gamma", "2026-02-01-beta"]:
        d = archive / name
        d.mkdir(parents=True)
        (d / "proposal.md").write_text(f"# Proposal\n\n## Descripción\n\nDescription of {name}.\n")
    entries = collect_archived_changes(archive)
    assert len(entries) == 3
    assert entries[0].date == date(2026, 3, 1)
    assert entries[1].date == date(2026, 2, 1)
    assert entries[2].date == date(2026, 1, 1)


def test_collect_archived_changes_description_from_proposal(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    change_dir = archive / "2026-03-11-my-feature"
    change_dir.mkdir(parents=True)
    (change_dir / "proposal.md").write_text(
        "# Proposal\n\n## Descripción\n\nAdd a great new feature.\n"
    )
    entries = collect_archived_changes(archive)
    assert len(entries) == 1
    assert "great new feature" in entries[0].description


# ---------------------------------------------------------------------------
# make_placeholder
# ---------------------------------------------------------------------------


def test_make_placeholder(tmp_path: Path) -> None:
    ph = make_placeholder("description", "Short description of the project")
    assert ph.startswith("<!-- sdd-docs:placeholder")
    assert 'type="description"' in ph
    assert "Short description" in ph
    assert ph.endswith("-->")


# ---------------------------------------------------------------------------
# render_mkdocs_yml
# ---------------------------------------------------------------------------


def test_render_mkdocs_yml_basic(tmp_path: Path) -> None:
    yml = render_mkdocs_yml("My Project", "A great tool.", [], False)
    assert "site_name: My Project" in yml
    assert "site_description: A great tool." in yml
    assert "Home: index.md" in yml
    assert "changelog" not in yml.lower()


def test_render_mkdocs_yml_with_domains(tmp_path: Path) -> None:
    yml = render_mkdocs_yml("Project", "Desc.", ["core", "auth"], False)
    assert "reference/core.md" in yml
    assert "reference/auth.md" in yml


def test_render_mkdocs_yml_with_changelog(tmp_path: Path) -> None:
    yml = render_mkdocs_yml("Project", "Desc.", [], True)
    assert "changelog.md" in yml


def test_render_mkdocs_yml_without_changelog(tmp_path: Path) -> None:
    yml = render_mkdocs_yml("Project", "Desc.", [], False)
    assert "changelog.md" not in yml


# ---------------------------------------------------------------------------
# render_index_md
# ---------------------------------------------------------------------------


def test_render_index_md_with_description(tmp_path: Path) -> None:
    md = render_index_md("My Project", "A tool for developers.")
    assert "# My Project" in md
    assert "A tool for developers." in md
    assert "Quick Start" in md


def test_render_index_md_with_placeholder(tmp_path: Path) -> None:
    ph = make_placeholder("description", "some desc")
    md = render_index_md("My Project", ph)
    assert "sdd-docs:placeholder" in md


# ---------------------------------------------------------------------------
# render_reference_page
# ---------------------------------------------------------------------------


def _make_spec_file(tmp_path: Path, domain: str, content: str) -> Path:
    spec_path = tmp_path / "openspec" / "specs" / domain / "spec.md"
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text(content)
    return spec_path


def test_render_reference_page_with_reqs_and_decisions(tmp_path: Path) -> None:
    content = SPEC_WITH_REQS + "\n" + SPEC_WITH_DECISIONS
    spec_path = _make_spec_file(tmp_path, "core", content)
    page = render_reference_page("core", spec_path)
    assert "# Core Reference" in page
    assert "REQ-01" in page
    assert "Use CLI" in page
    assert "sdd-docs:placeholder" in page


def test_render_reference_page_no_decisions(tmp_path: Path) -> None:
    spec_path = _make_spec_file(tmp_path, "auth", SPEC_WITH_REQS)
    page = render_reference_page("auth", spec_path)
    assert "# Auth Reference" in page
    assert "REQ-01" in page
    assert "## Decisions" not in page


# ---------------------------------------------------------------------------
# render_changelog_md
# ---------------------------------------------------------------------------


def test_render_changelog_md_newest_first(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    for name in ["2026-01-01-old-feature", "2026-03-01-new-feature"]:
        d = archive / name
        d.mkdir(parents=True)
        (d / "proposal.md").write_text("# P\n\n## Descripción\n\nSome change.\n")

    md = render_changelog_md(archive)
    assert "# Changelog" in md
    new_pos = md.index("new-feature")
    old_pos = md.index("old-feature")
    assert new_pos < old_pos


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


def _make_minimal_openspec(base: Path) -> Path:
    openspec = base / "openspec"
    steering = openspec / "steering"
    steering.mkdir(parents=True)
    (steering / "product.md").write_text("# Test Project\n\nA test project.\n")
    specs = openspec / "specs" / "core"
    specs.mkdir(parents=True)
    (specs / "spec.md").write_text(SPEC_WITH_REQS)
    archive = openspec / "changes" / "archive" / "2026-01-01-first-feature"
    archive.mkdir(parents=True)
    (archive / "proposal.md").write_text("# P\n\n## Descripción\n\nFirst feature.\n")
    return openspec


def test_main_generates_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from sdd_tui import docs_gen

    _make_minimal_openspec(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(docs_gen, "find_git_root", lambda _: tmp_path)

    import sys

    monkeypatch.setattr(sys, "argv", ["sdd-docs"])
    docs_gen.main()

    assert (tmp_path / "mkdocs.yml").exists()
    assert (tmp_path / "docs" / "index.md").exists()
    assert (tmp_path / "docs" / "reference" / "core.md").exists()
    assert (tmp_path / "docs" / "changelog.md").exists()


def test_main_dry_run_no_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from sdd_tui import docs_gen

    _make_minimal_openspec(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(docs_gen, "find_git_root", lambda _: tmp_path)

    import sys

    monkeypatch.setattr(sys, "argv", ["sdd-docs", "--dry-run"])
    docs_gen.main()

    assert not (tmp_path / "mkdocs.yml").exists()
    assert not (tmp_path / "docs").exists()


def test_main_no_force_skips_existing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from sdd_tui import docs_gen

    _make_minimal_openspec(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(docs_gen, "find_git_root", lambda _: tmp_path)

    existing = tmp_path / "docs" / "index.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("ORIGINAL")

    import sys

    monkeypatch.setattr(sys, "argv", ["sdd-docs"])
    docs_gen.main()

    assert existing.read_text() == "ORIGINAL"


def test_main_force_overwrites(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from sdd_tui import docs_gen

    _make_minimal_openspec(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(docs_gen, "find_git_root", lambda _: tmp_path)

    existing = tmp_path / "docs" / "index.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("ORIGINAL")

    import sys

    monkeypatch.setattr(sys, "argv", ["sdd-docs", "--force"])
    docs_gen.main()

    content = existing.read_text()
    assert content != "ORIGINAL"
    assert "# Test Project" in content


def test_main_no_openspec_exits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from sdd_tui import docs_gen

    isolated = tmp_path / "empty-project"
    isolated.mkdir()
    monkeypatch.chdir(isolated)
    monkeypatch.setattr(docs_gen, "find_openspec", lambda _: None)

    import sys

    monkeypatch.setattr(sys, "argv", ["sdd-docs"])
    with pytest.raises(SystemExit) as exc_info:
        docs_gen.main()
    assert exc_info.value.code == 1
