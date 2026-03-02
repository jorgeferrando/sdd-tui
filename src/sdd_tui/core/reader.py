from __future__ import annotations

from pathlib import Path

from sdd_tui.core.models import Change, OpenspecNotFoundError, Pipeline


class OpenspecReader:
    def load(self, openspec_path: Path) -> list[Change]:
        changes_path = openspec_path / "changes"
        if not openspec_path.exists() or not changes_path.exists():
            raise OpenspecNotFoundError(f"openspec/ not found at {openspec_path}")

        entries = sorted(
            entry for entry in changes_path.iterdir()
            if entry.is_dir() and entry.name != "archive"
        )

        return [
            Change(name=entry.name, path=entry, pipeline=Pipeline())
            for entry in entries
        ]
