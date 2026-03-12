from pathlib import Path

from sdd_tui.core.providers.protocol import GitWorkflowConfig
from sdd_tui.core.reader import (
    _parse_git_workflow,
    _write_git_workflow_config,
    load_git_workflow_config,
)

# --- load_git_workflow_config ---


def test_load_returns_defaults_when_file_missing(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    result = load_git_workflow_config(openspec)
    assert result == GitWorkflowConfig()


def test_load_returns_defaults_when_no_git_workflow_section(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    (openspec / "config.yaml").write_text("projects:\n  - path: /some/path\n")
    result = load_git_workflow_config(openspec)
    assert result == GitWorkflowConfig()


def test_load_parses_complete_config(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    (openspec / "config.yaml").write_text(
        "git_workflow:\n"
        "  issue_tracker: github\n"
        "  git_host: github\n"
        "  branching_model: github-flow\n"
        "  change_prefix: feature\n"
        "  changelog_format: labels\n"
    )
    result = load_git_workflow_config(openspec)
    assert result.issue_tracker == "github"
    assert result.git_host == "github"
    assert result.branching_model == "github-flow"
    assert result.change_prefix == "feature"
    assert result.changelog_format == "labels"


def test_load_applies_defaults_for_missing_fields(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    (openspec / "config.yaml").write_text(
        "git_workflow:\n"
        "  git_host: github\n"
    )
    result = load_git_workflow_config(openspec)
    assert result.git_host == "github"
    assert result.issue_tracker == "none"  # default
    assert result.change_prefix == "issue"  # default


def test_load_returns_defaults_on_corrupt_file(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    # Trigger an exception during parsing by making read_text fail
    config_file = openspec / "config.yaml"
    config_file.write_text("git_workflow:\n  git_host: github\n")
    # Patch to simulate a bad parse
    from unittest.mock import patch

    with patch("sdd_tui.core.reader._parse_git_workflow", side_effect=RuntimeError("boom")):
        result = load_git_workflow_config(openspec)
    assert result == GitWorkflowConfig()


# --- _parse_git_workflow ---


def test_parse_git_workflow_ignores_unknown_keys() -> None:
    text = "git_workflow:\n  git_host: github\n  unknown_key: value\n"
    result = _parse_git_workflow(text)
    assert result.git_host == "github"
    assert not hasattr(result, "unknown_key")


def test_parse_git_workflow_stops_at_next_top_level_key() -> None:
    text = (
        "git_workflow:\n"
        "  git_host: github\n"
        "projects:\n"
        "  - path: /foo\n"
    )
    result = _parse_git_workflow(text)
    assert result.git_host == "github"


# --- _write_git_workflow_config ---


def test_write_creates_new_file(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    cfg = GitWorkflowConfig(git_host="github", issue_tracker="github")
    _write_git_workflow_config(openspec, cfg)

    content = (openspec / "config.yaml").read_text()
    assert "git_workflow:" in content
    assert "git_host: github" in content
    assert "issue_tracker: github" in content


def test_write_replaces_existing_section(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    (openspec / "config.yaml").write_text(
        "# header\n"
        "git_workflow:\n"
        "  git_host: none\n"
        "  issue_tracker: none\n"
        "  branching_model: github-flow\n"
        "  change_prefix: issue\n"
        "  changelog_format: both\n"
    )
    cfg = GitWorkflowConfig(git_host="github", issue_tracker="github")
    _write_git_workflow_config(openspec, cfg)

    content = (openspec / "config.yaml").read_text()
    assert "git_host: github" in content
    assert "git_host: none" not in content
    assert "# header" in content  # preserved


def test_write_appends_section_when_absent(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec"
    openspec.mkdir()
    (openspec / "config.yaml").write_text("projects:\n  - path: /foo\n")
    cfg = GitWorkflowConfig(git_host="github")
    _write_git_workflow_config(openspec, cfg)

    content = (openspec / "config.yaml").read_text()
    assert "projects:" in content
    assert "git_workflow:" in content
    assert "git_host: github" in content


def test_write_creates_parent_dir_if_needed(tmp_path: Path) -> None:
    openspec = tmp_path / "openspec" / "nested"
    cfg = GitWorkflowConfig()
    _write_git_workflow_config(openspec, cfg)
    assert (openspec / "config.yaml").exists()
