from __future__ import annotations

import json
import re
from pathlib import Path

from sdd_tui.core.config import AppConfig
from sdd_tui.core.models import Change, OpenspecNotFoundError
from sdd_tui.core.providers.protocol import GitWorkflowConfig


def load_git_workflow_config(openspec_path: Path) -> GitWorkflowConfig:
    """Read the git_workflow: section from openspec/config.yaml, returning defaults on any error."""
    config_file = openspec_path / "config.yaml"
    if not config_file.exists():
        return GitWorkflowConfig()
    try:
        return _parse_git_workflow(config_file.read_text(errors="replace"))
    except Exception:
        return GitWorkflowConfig()


def _parse_git_workflow(text: str) -> GitWorkflowConfig:
    defaults = GitWorkflowConfig()
    kwargs: dict[str, str] = {}
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "git_workflow:":
            in_section = True
            continue
        if in_section:
            if not stripped or stripped.startswith("#"):
                continue
            # End of section when a new top-level key appears (no leading whitespace)
            if line and not line[0].isspace():
                break
            m = re.match(r"\s+(\w+):\s*(.+)", line)
            if m:
                kwargs[m.group(1)] = m.group(2).strip()
    # Only set fields that exist on GitWorkflowConfig
    valid = {f for f in defaults.__dataclass_fields__}
    filtered = {k: v for k, v in kwargs.items() if k in valid}
    return GitWorkflowConfig(**filtered)


def _write_git_workflow_config(openspec_path: Path, cfg: GitWorkflowConfig) -> None:
    """Write or replace the git_workflow: section in openspec/config.yaml."""
    config_file = openspec_path / "config.yaml"

    block_lines = [
        "git_workflow:",
        f"  issue_tracker: {cfg.issue_tracker}",
        f"  git_host: {cfg.git_host}",
        f"  branching_model: {cfg.branching_model}",
        f"  change_prefix: {cfg.change_prefix}",
        f"  changelog_format: {cfg.changelog_format}",
    ]
    block = "\n".join(block_lines) + "\n"

    if not config_file.exists():
        openspec_path.mkdir(parents=True, exist_ok=True)
        config_file.write_text("# Añadir jira_prefix: si usas SDD\n" + block)
        return

    existing = config_file.read_text(errors="replace")
    lines = existing.splitlines(keepends=True)

    # Find start and end of existing git_workflow: section
    start = None
    end = len(lines)
    for i, line in enumerate(lines):
        if line.strip() == "git_workflow:":
            start = i
            continue
        if start is not None and i > start:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if line and not line[0].isspace():
                end = i
                break

    if start is not None:
        new_lines = lines[:start] + [block] + lines[end:]
        config_file.write_text("".join(new_lines))
    else:
        # Append at the end, ensuring a newline separator
        if existing and not existing.endswith("\n"):
            existing += "\n"
        config_file.write_text(existing + block)


def load_steering(openspec_path: Path) -> str | None:
    """Return content of openspec/steering.md, or None if not present."""
    path = openspec_path / "steering.md"
    if not path.exists():
        return None
    return path.read_text(errors="replace")


def load_spec_json(change_path: Path) -> dict | None:
    """Return parsed spec.json for a change, or None if missing or malformed."""
    path = change_path / "spec.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(errors="replace"))
    except (json.JSONDecodeError, OSError):
        return None


class OpenspecReader:
    def load(
        self,
        openspec_path: Path,
        include_archived: bool = False,
        project_path: Path | None = None,
    ) -> list[Change]:
        changes_path = openspec_path / "changes"
        if not openspec_path.exists() or not changes_path.exists():
            raise OpenspecNotFoundError(f"openspec/ not found at {openspec_path}")

        proj = project_path or openspec_path.parent

        entries = sorted(
            entry for entry in changes_path.iterdir() if entry.is_dir() and entry.name != "archive"
        )
        changes = [
            Change(name=entry.name, path=entry, project=proj.name, project_path=proj)
            for entry in entries
        ]

        if include_archived:
            archive_path = changes_path / "archive"
            if archive_path.exists():
                archived_entries = sorted(
                    entry for entry in archive_path.iterdir() if entry.is_dir()
                )
                changes += [
                    Change(
                        name=entry.name,
                        path=entry,
                        archived=True,
                        project=proj.name,
                        project_path=proj,
                    )
                    for entry in archived_entries
                ]

        return changes


def load_all_changes(config: AppConfig, cwd: Path, include_archived: bool = False) -> list[Change]:
    """Return flat list of Changes from all configured projects.

    If config.projects is empty, falls back to single-project mode using cwd.
    Projects whose openspec/ is missing are skipped silently.
    """
    reader = OpenspecReader()
    if not config.projects:
        return reader.load(cwd / "openspec", include_archived, project_path=cwd)

    all_changes: list[Change] = []
    for pc in config.projects:
        try:
            all_changes.extend(
                reader.load(pc.path / "openspec", include_archived, project_path=pc.path)
            )
        except OpenspecNotFoundError:
            pass
    return all_changes
