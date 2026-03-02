from __future__ import annotations

import sys
from pathlib import Path

from textual.app import App, ComposeResult

from sdd_tui.core.git_reader import GitReader
from sdd_tui.core.models import Change, OpenspecNotFoundError
from sdd_tui.core.pipeline import PipelineInferer
from sdd_tui.core.reader import OpenspecReader
from sdd_tui.tui.epics import EpicsView


class SddTuiApp(App):
    CSS = """
    EpicsView {
        height: 1fr;
    }
    """

    def __init__(self, openspec_path: Path) -> None:
        super().__init__()
        self._openspec_path = openspec_path
        self._reader = OpenspecReader()
        self._inferer = PipelineInferer()
        self._git = GitReader()

    def compose(self) -> ComposeResult:
        changes = self._load_changes()
        yield EpicsView(changes)

    def refresh_changes(self) -> None:
        changes = self._load_changes()
        self.query_one(EpicsView).update(changes)

    def _load_changes(self) -> list[Change]:
        changes = self._reader.load(self._openspec_path)
        for change in changes:
            change.pipeline = self._inferer.infer(change.path, self._git)
        return changes


def main() -> None:
    openspec_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "openspec"

    if not openspec_path.exists():
        print(f"Error: openspec/ not found at {openspec_path}", file=sys.stderr)
        sys.exit(1)

    try:
        app = SddTuiApp(openspec_path)
        app.run()
    except OpenspecNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
