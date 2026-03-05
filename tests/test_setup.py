"""Tests for sdd-setup CLI (src/sdd_tui/setup.py)."""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sdd_tui.setup import (
    _check_claude_in_path,
    _fetch_and_install,
    _print_summary,
    _prompt_conflict,
    _resolve_destination,
    _run_check,
)

# ---------------------------------------------------------------------------
# _resolve_destination
# ---------------------------------------------------------------------------


def test_resolve_destination_global() -> None:
    args = argparse.Namespace(global_=True, local=False)
    result = _resolve_destination(args)
    assert result == Path.home() / ".claude" / "skills"


def test_resolve_destination_local() -> None:
    args = argparse.Namespace(global_=False, local=True)
    result = _resolve_destination(args)
    assert result == Path.cwd() / ".claude" / "skills"


def test_resolve_destination_interactive_choice_1(capsys: pytest.CaptureFixture) -> None:
    args = argparse.Namespace(global_=False, local=False)
    with patch("builtins.input", return_value="1"):
        result = _resolve_destination(args)
    assert result == Path.home() / ".claude" / "skills"


def test_resolve_destination_interactive_choice_2() -> None:
    args = argparse.Namespace(global_=False, local=False)
    with patch("builtins.input", return_value="2"):
        result = _resolve_destination(args)
    assert result == Path.cwd() / ".claude" / "skills"


def test_resolve_destination_interactive_invalid_returns_none(
    capsys: pytest.CaptureFixture,
) -> None:
    args = argparse.Namespace(global_=False, local=False)
    with patch("builtins.input", return_value="9"):
        result = _resolve_destination(args)
    assert result is None


def test_resolve_destination_eof_returns_none() -> None:
    args = argparse.Namespace(global_=False, local=False)
    with patch("builtins.input", side_effect=EOFError):
        result = _resolve_destination(args)
    assert result is None


# ---------------------------------------------------------------------------
# _prompt_conflict
# ---------------------------------------------------------------------------


def test_prompt_conflict_update() -> None:
    with patch("builtins.input", return_value="u"):
        result = _prompt_conflict("sdd-init")
    assert result == "update"


def test_prompt_conflict_skip() -> None:
    with patch("builtins.input", return_value="s"):
        result = _prompt_conflict("sdd-init")
    assert result == "skip"


def test_prompt_conflict_unknown_input_defaults_to_skip() -> None:
    with patch("builtins.input", return_value="x"):
        result = _prompt_conflict("sdd-init")
    assert result == "skip"


def test_prompt_conflict_eof_defaults_to_skip() -> None:
    with patch("builtins.input", side_effect=EOFError):
        result = _prompt_conflict("sdd-init")
    assert result == "skip"


# ---------------------------------------------------------------------------
# _fetch_and_install
# ---------------------------------------------------------------------------


def _make_skill(skills_dir: Path, name: str) -> None:
    skill_path = skills_dir / name
    skill_path.mkdir(parents=True)
    (skill_path / "SKILL.md").write_text(f"# {name}")


def test_install_new_skill(tmp_path: Path) -> None:
    """REQ-SETUP03/REQ-SETUP04: new skill → installed, no conflict prompt."""
    dest = tmp_path / "dest"
    dest.mkdir()
    fake_clone = tmp_path / "clone"
    skills_src = fake_clone / "skills"
    _make_skill(skills_src, "sdd-init")

    with (
        patch("sdd_tui.setup._clone_repo") as mock_clone,
        patch("tempfile.mkdtemp", return_value=str(fake_clone)),
    ):
        mock_clone.return_value = None
        installed, updated, skipped = _fetch_and_install(dest)

    assert installed == ["sdd-init"]
    assert updated == []
    assert skipped == []
    assert (dest / "sdd-init" / "SKILL.md").exists()


def test_install_skill_conflict_update(tmp_path: Path) -> None:
    """REQ-SETUP03/REQ-SETUP04: existing skill + user chooses update → overwrite."""
    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / "sdd-init").mkdir()
    (dest / "sdd-init" / "SKILL.md").write_text("old content")

    fake_clone = tmp_path / "clone"
    skills_src = fake_clone / "skills"
    _make_skill(skills_src, "sdd-init")

    with (
        patch("sdd_tui.setup._clone_repo"),
        patch("tempfile.mkdtemp", return_value=str(fake_clone)),
        patch("sdd_tui.setup._prompt_conflict", return_value="update"),
    ):
        installed, updated, skipped = _fetch_and_install(dest)

    assert updated == ["sdd-init"]
    assert installed == []
    assert skipped == []
    assert (dest / "sdd-init" / "SKILL.md").read_text() == "# sdd-init"


def test_install_skill_conflict_skip(tmp_path: Path) -> None:
    """REQ-SETUP03/REQ-SETUP05: existing skill + user chooses skip → unchanged."""
    dest = tmp_path / "dest"
    dest.mkdir()
    (dest / "sdd-init").mkdir()
    (dest / "sdd-init" / "SKILL.md").write_text("old content")

    fake_clone = tmp_path / "clone"
    skills_src = fake_clone / "skills"
    _make_skill(skills_src, "sdd-init")

    with (
        patch("sdd_tui.setup._clone_repo"),
        patch("tempfile.mkdtemp", return_value=str(fake_clone)),
        patch("sdd_tui.setup._prompt_conflict", return_value="skip"),
    ):
        installed, updated, skipped = _fetch_and_install(dest)

    assert skipped == ["sdd-init"]
    assert (dest / "sdd-init" / "SKILL.md").read_text() == "old content"


def test_install_multiple_skills_sorted(tmp_path: Path) -> None:
    """Skills are processed in sorted order."""
    dest = tmp_path / "dest"
    dest.mkdir()
    fake_clone = tmp_path / "clone"
    skills_src = fake_clone / "skills"
    _make_skill(skills_src, "sdd-tasks")
    _make_skill(skills_src, "sdd-apply")
    _make_skill(skills_src, "sdd-init")

    with (
        patch("sdd_tui.setup._clone_repo"),
        patch("tempfile.mkdtemp", return_value=str(fake_clone)),
    ):
        installed, updated, skipped = _fetch_and_install(dest)

    assert installed == ["sdd-apply", "sdd-init", "sdd-tasks"]


def test_tmp_dir_cleaned_up_after_install(tmp_path: Path) -> None:
    """Temp directory is removed after install even on success."""
    dest = tmp_path / "dest"
    dest.mkdir()
    fake_clone = tmp_path / "clone"
    (fake_clone / "skills").mkdir(parents=True)

    with (
        patch("sdd_tui.setup._clone_repo"),
        patch("tempfile.mkdtemp", return_value=str(fake_clone)),
    ):
        _fetch_and_install(dest)

    assert not fake_clone.exists()


# ---------------------------------------------------------------------------
# _check_claude_in_path
# ---------------------------------------------------------------------------


def test_claude_not_in_path_prints_warning(capsys: pytest.CaptureFixture) -> None:
    """REQ-SETUP07: claude missing → informational warning, no exception."""
    with patch("sdd_tui.setup.subprocess.run", side_effect=FileNotFoundError):
        _check_claude_in_path()  # must not raise

    out = capsys.readouterr().out
    assert "Claude Code not found" in out


def test_claude_in_path_no_warning(capsys: pytest.CaptureFixture) -> None:
    """REQ-SETUP07: claude present → no warning."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("sdd_tui.setup.subprocess.run", return_value=mock_result):
        _check_claude_in_path()

    out = capsys.readouterr().out
    assert "Claude Code not found" not in out


# ---------------------------------------------------------------------------
# _print_summary
# ---------------------------------------------------------------------------


def test_print_summary_shows_counts(capsys: pytest.CaptureFixture, tmp_path: Path) -> None:
    """REQ-SETUP08: summary shows installed/updated/skipped counts and next steps."""
    _print_summary(["sdd-init"], ["sdd-apply"], ["sdd-tasks"], tmp_path)
    out = capsys.readouterr().out
    assert "installed: 1" in out
    assert "updated: 1" in out
    assert "skipped: 1" in out
    assert "Restart Claude Code" in out
    assert "/sdd-init" in out


# ---------------------------------------------------------------------------
# _run_check
# ---------------------------------------------------------------------------


def test_run_check_shows_version(capsys: pytest.CaptureFixture, tmp_path: Path) -> None:
    """REQ-SETUP11: --check shows package version and skills source."""
    with (
        patch("importlib.metadata.version", return_value="1.2.3"),
        patch("sdd_tui.setup.Path.home", return_value=tmp_path),
        patch("sdd_tui.setup.Path.cwd", return_value=tmp_path),
    ):
        _run_check()

    out = capsys.readouterr().out
    assert "1.2.3" in out
    assert "github.com/jorgeferrando/sdd-tui" in out


def test_run_check_lists_installed_skills(capsys: pytest.CaptureFixture, tmp_path: Path) -> None:
    """REQ-SETUP11: --check lists installed skills per location."""
    global_skills = tmp_path / ".claude" / "skills"
    _make_skill(global_skills, "sdd-init")
    _make_skill(global_skills, "sdd-apply")

    with (
        patch("importlib.metadata.version", return_value="0.1.0"),
        patch("sdd_tui.setup.Path.home", return_value=tmp_path),
        patch("sdd_tui.setup.Path.cwd", return_value=tmp_path / "project"),
    ):
        _run_check()

    out = capsys.readouterr().out
    assert "sdd-apply" in out
    assert "sdd-init" in out
