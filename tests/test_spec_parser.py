from __future__ import annotations

from datetime import date
from pathlib import Path

from sdd_tui.core.spec_parser import (
    Decision,
    collect_archived_decisions,
    extract_decisions,
    parse_delta,
)

# ---------------------------------------------------------------------------
# parse_delta
# ---------------------------------------------------------------------------


def test_parse_delta_with_markers(tmp_path: Path) -> None:
    spec = tmp_path / "spec.md"
    spec.write_text(
        "## ADDED Requirements\n"
        "- **REQ-01** `[Event]` When X...\n"
        "\n"
        "## MODIFIED Requirements\n"
        "- **REQ-03** — Before: old After: new\n"
        "\n"
        "## REMOVED Requirements\n"
        "- **REQ-02** — Removed because: legacy\n"
    )
    delta = parse_delta(spec)
    assert delta.fallback is False
    assert any("REQ-01" in line for line in delta.added)
    assert any("REQ-03" in line for line in delta.modified)
    assert any("REQ-02" in line for line in delta.removed)


def test_parse_delta_fallback_no_markers(tmp_path: Path) -> None:
    spec = tmp_path / "spec.md"
    spec.write_text("# Regular spec\n\nSome content without markers.\n")
    delta = parse_delta(spec)
    assert delta.fallback is True
    assert delta.added == []
    assert delta.modified == []
    assert delta.removed == []


def test_parse_delta_case_insensitive(tmp_path: Path) -> None:
    spec = tmp_path / "spec.md"
    spec.write_text(
        "## added Requirements\n- **REQ-01** line\n## modified requirements\n- **REQ-02** line\n"
    )
    delta = parse_delta(spec)
    assert delta.fallback is False
    assert len(delta.added) >= 1
    assert len(delta.modified) >= 1


def test_parse_delta_preserves_blank_lines(tmp_path: Path) -> None:
    spec = tmp_path / "spec.md"
    spec.write_text("## ADDED Requirements\n- **REQ-01** first\n\n- **REQ-02** second\n")
    delta = parse_delta(spec)
    assert "" in delta.added  # blank line preserved


# ---------------------------------------------------------------------------
# extract_decisions
# ---------------------------------------------------------------------------


def test_extract_decisions_with_table(tmp_path: Path) -> None:
    design = tmp_path / "design.md"
    design.write_text(
        "## Decisiones Tomadas\n"
        "\n"
        "| Decisión | Alternativa Descartada | Motivo |\n"
        "|---------|----------------------|--------|\n"
        "| Use X | Use Y | X is simpler |\n"
        "| Keep Z | Remove Z | Backward compat |\n"
    )
    cd = extract_decisions(design, "my-change")
    assert cd.change_name == "my-change"
    assert len(cd.decisions) == 2
    assert cd.decisions[0] == Decision("Use X", "Use Y", "X is simpler")
    assert cd.decisions[1] == Decision("Keep Z", "Remove Z", "Backward compat")


def test_extract_decisions_diseno_heading(tmp_path: Path) -> None:
    design = tmp_path / "design.md"
    design.write_text(
        "## Decisiones de Diseño\n"
        "\n"
        "| Decisión | Alternativa Descartada | Motivo |\n"
        "|---------|----------------------|--------|\n"
        "| Use X | Use Y | simpler |\n"
    )
    cd = extract_decisions(design, "my-change")
    assert len(cd.decisions) == 1
    assert cd.decisions[0].decision == "Use X"


def test_extract_decisions_no_table(tmp_path: Path) -> None:
    design = tmp_path / "design.md"
    design.write_text("# Design\n\nNo decisions section here.\n")
    cd = extract_decisions(design, "my-change")
    assert cd.decisions == []


def test_extract_decisions_missing_file(tmp_path: Path) -> None:
    cd = extract_decisions(tmp_path / "nonexistent.md", "ghost-change")
    assert cd.change_name == "ghost-change"
    assert cd.decisions == []


def test_extract_decisions_three_cols_defaults_locked(tmp_path: Path) -> None:
    """REQ-DSB-03: 3-col table rows get status='locked' by default."""
    design = tmp_path / "design.md"
    design.write_text(
        "## Decisiones Tomadas\n"
        "\n"
        "| Decisión | Alternativa | Motivo |\n"
        "|---------|------------|--------|\n"
        "| Use X | Use Y | simpler |\n"
    )
    cd = extract_decisions(design, "my-change")
    assert cd.decisions[0].status == "locked"


def test_extract_decisions_with_status_column(tmp_path: Path) -> None:
    """REQ-DSB-02: 4-col table rows parse status from 4th column."""
    design = tmp_path / "design.md"
    design.write_text(
        "## Decisiones Tomadas\n"
        "\n"
        "| Decisión | Alternativa | Motivo | Estado |\n"
        "|---------|------------|--------|--------|\n"
        "| Use X | Use Y | simpler | locked |\n"
        "| Schema v2 | Schema v1 | perf | open |\n"
        "| Add cache | No cache | TBD | deferred |\n"
    )
    cd = extract_decisions(design, "my-change")
    assert len(cd.decisions) == 3
    assert cd.decisions[0].status == "locked"
    assert cd.decisions[1].status == "open"
    assert cd.decisions[2].status == "deferred"


def test_extract_decisions_unknown_status_stored_as_is(tmp_path: Path) -> None:
    """REQ-DSB-04: unknown status values are stored without error."""
    design = tmp_path / "design.md"
    design.write_text(
        "## Decisiones Tomadas\n"
        "\n"
        "| Decisión | Alternativa | Motivo | Estado |\n"
        "|---------|------------|--------|--------|\n"
        "| Use X | Use Y | simpler | experimental |\n"
    )
    cd = extract_decisions(design, "my-change")
    assert cd.decisions[0].status == "experimental"


# ---------------------------------------------------------------------------
# collect_archived_decisions
# ---------------------------------------------------------------------------


def test_collect_archived_decisions_order(tmp_path: Path) -> None:
    archive = tmp_path / "archive"

    # Create two archived changes
    for dirname, content in [
        (
            "2026-02-01-view-2-change-detail",
            "| Use DataTable | ListView | row selection |\n",
        ),
        (
            "2026-03-04-view-8-spec-health",
            "| REQ count unique | count occurrences | accuracy |\n",
        ),
    ]:
        d = archive / dirname
        d.mkdir(parents=True)
        (d / "design.md").write_text(
            "## Decisiones Tomadas\n\n"
            "| Decisión | Alternativa Descartada | Motivo |\n"
            "|---------|----------------------|--------|\n" + content
        )

    results = collect_archived_decisions(archive)
    assert len(results) == 2
    assert results[0].change_name == "view-2-change-detail"
    assert results[0].archive_date == date(2026, 2, 1)
    assert results[1].change_name == "view-8-spec-health"
    assert results[1].archive_date == date(2026, 3, 4)


def test_collect_archived_decisions_skip_invalid_prefix(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()
    # Directory without date prefix — must be skipped silently
    (archive / "not-a-dated-dir").mkdir()
    results = collect_archived_decisions(archive)
    assert results == []


def test_collect_archived_decisions_empty_archive(tmp_path: Path) -> None:
    results = collect_archived_decisions(tmp_path / "nonexistent")
    assert results == []
