from __future__ import annotations

from pathlib import Path

from sdd_tui.core.models import Change, OpenspecNotFoundError, Pipeline


class OpenspecReader:
    def load(self, openspec_path: Path, include_archived: bool = False) -> list[Change]:
        changes_path = openspec_path / "changes"
        if not openspec_path.exists() or not changes_path.exists():
            raise OpenspecNotFoundError(f"openspec/ not found at {openspec_path}")

        entries = sorted(
            entry for entry in changes_path.iterdir()
            if entry.is_dir() and entry.name != "archive"
        )
        changes = [Change(name=entry.name, path=entry) for entry in entries]

        if include_archived:
            archive_path = changes_path / "archive"
            if archive_path.exists():
                archived_entries = sorted(
                    entry for entry in archive_path.iterdir()
                    if entry.is_dir()
                )
                changes += [
                    Change(name=entry.name, path=entry, archived=True)
                    for entry in archived_entries
                ]

        return changes
