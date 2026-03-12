from __future__ import annotations

from pathlib import Path

from sdd_tui.core.milestones import Milestone, _parse_milestones, load_milestones


def test_load_milestones_no_file(tmp_path: Path) -> None:
    """REQ-ML-02: returns [] if milestones.yaml does not exist."""
    result = load_milestones(tmp_path)
    assert result == []


def test_load_milestones_empty_file(tmp_path: Path) -> None:
    """REQ-ML-02: returns [] for empty file."""
    (tmp_path / "milestones.yaml").write_text("")
    result = load_milestones(tmp_path)
    assert result == []


def test_parse_milestones_basic() -> None:
    """REQ-ML-01: parses two milestones with their changes."""
    text = """\
milestones:
  - name: "v1.0 — Bootstrap"
    changes:
      - bootstrap
      - view-2-change-detail
  - name: "v1.1 — UX"
    changes:
      - ux-feedback
      - ux-navigation
"""
    result = _parse_milestones(text)
    assert len(result) == 2
    assert result[0] == Milestone(
        name="v1.0 — Bootstrap", changes=["bootstrap", "view-2-change-detail"]
    )
    assert result[1] == Milestone(name="v1.1 — UX", changes=["ux-feedback", "ux-navigation"])


def test_parse_milestones_single_milestone() -> None:
    """REQ-ML-01: single milestone."""
    text = """\
milestones:
  - name: "v1.0"
    changes:
      - bootstrap
"""
    result = _parse_milestones(text)
    assert len(result) == 1
    assert result[0].name == "v1.0"
    assert result[0].changes == ["bootstrap"]


def test_parse_milestones_empty_changes() -> None:
    """REQ-ML-04: milestone with no changes list → changes=[]."""
    text = """\
milestones:
  - name: "Empty"
"""
    result = _parse_milestones(text)
    assert len(result) == 1
    assert result[0].name == "Empty"
    assert result[0].changes == []


def test_parse_milestones_quoted_name_double() -> None:
    """REQ-ML-01: double-quoted name is stripped of quotes."""
    text = 'milestones:\n  - name: "My Milestone"\n'
    result = _parse_milestones(text)
    assert result[0].name == "My Milestone"


def test_parse_milestones_quoted_name_single() -> None:
    """REQ-ML-01: single-quoted name is stripped of quotes."""
    text = "milestones:\n  - name: 'My Milestone'\n"
    result = _parse_milestones(text)
    assert result[0].name == "My Milestone"


def test_parse_milestones_name_with_em_dash() -> None:
    """REQ-ML-01: name with unicode em dash preserved."""
    text = 'milestones:\n  - name: "v1.0 — Bootstrap"\n'
    result = _parse_milestones(text)
    assert result[0].name == "v1.0 — Bootstrap"


def test_load_milestones_malformed(tmp_path: Path) -> None:
    """REQ-ML-03: returns [] without raising for malformed content."""
    (tmp_path / "milestones.yaml").write_text(":::invalid:::\n")
    result = load_milestones(tmp_path)
    assert result == []


def test_parse_milestones_preserves_order() -> None:
    """REQ-ML-01: milestone order matches YAML declaration order."""
    text = """\
milestones:
  - name: "First"
    changes:
      - alpha
  - name: "Second"
    changes:
      - beta
  - name: "Third"
    changes:
      - gamma
"""
    result = _parse_milestones(text)
    assert [m.name for m in result] == ["First", "Second", "Third"]


def test_parse_milestones_ignores_comments() -> None:
    """REQ-ML-05: lines starting with # are ignored."""
    text = """\
milestones:
  # this is a comment
  - name: "v1.0"
    changes:
      # another comment
      - bootstrap
"""
    result = _parse_milestones(text)
    assert len(result) == 1
    assert result[0].changes == ["bootstrap"]
