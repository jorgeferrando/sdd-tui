from __future__ import annotations

import json
from pathlib import Path

from sdd_tui.core.config import AppConfig
from sdd_tui.core.models import Change, OpenspecNotFoundError


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


def load_all_changes(
    config: AppConfig, cwd: Path, include_archived: bool = False
) -> list[Change]:
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
