from __future__ import annotations

import sys
from pathlib import Path

from textual.app import App, ComposeResult

from sdd_tui.core.git_reader import GitReader
from sdd_tui.core.models import Change, OpenspecNotFoundError, Task, TaskGitState
from sdd_tui.core.pipeline import PipelineInferer, TaskParser
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
        self._parser = TaskParser()
        self._git = GitReader()

    def compose(self) -> ComposeResult:
        changes = self._load_changes()
        yield EpicsView(changes)

    def refresh_changes(self, include_archived: bool = False) -> list[Change]:
        changes = self._load_changes(include_archived)
        self.query_one(EpicsView).update(changes)
        return changes

    def _load_changes(self, include_archived: bool = False) -> list[Change]:
        changes = self._reader.load(self._openspec_path, include_archived)
        for change in changes:
            change.pipeline = self._inferer.infer(change.path, self._git)
            change.tasks = self._load_tasks(change)
        return changes

    def _load_tasks(self, change: Change) -> list[Task]:
        tasks_md = change.path / "tasks.md"
        if not tasks_md.exists():
            return []
        tasks = self._parser.parse(tasks_md)
        for task in tasks:
            if task.commit_hint:
                commit_info = self._git.find_commit(task.commit_hint, change.path)
                if commit_info:
                    task.git_state = TaskGitState.COMMITTED
                    task.commit = commit_info
        return tasks


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
