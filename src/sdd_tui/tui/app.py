from __future__ import annotations

import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding

from sdd_tui.core.config import AppConfig
from sdd_tui.core.git_reader import GitReader
from sdd_tui.core.models import Change, OpenspecNotFoundError, Task, TaskGitState
from sdd_tui.core.pipeline import PipelineInferer, TaskParser
from sdd_tui.core.providers.protocol import make_git_host, make_issue_tracker
from sdd_tui.core.reader import load_all_changes, load_git_workflow_config
from sdd_tui.tui.epics import EpicsView


class SddTuiApp(App):
    BINDINGS = [
        Binding("question_mark", "help", "Help", priority=True),
        Binding("ctrl+p", "skill_palette", "Skills", priority=True),
    ]

    CSS = """
    EpicsView {
        height: 1fr;
    }
    """

    def __init__(self, openspec_path: Path, config: AppConfig | None = None) -> None:
        super().__init__()
        self._openspec_path = openspec_path
        self._config = config or AppConfig()
        self._inferer = PipelineInferer()
        self._parser = TaskParser()
        self._git = GitReader()
        _wf_cfg = load_git_workflow_config(openspec_path)
        self._git_host = make_git_host(_wf_cfg)
        self._issue_tracker = make_issue_tracker(_wf_cfg)

    def on_mount(self) -> None:
        from sdd_tui.core.deps import check_deps
        from sdd_tui.tui.error_screen import ErrorScreen

        missing_required, missing_optional = check_deps()

        if missing_required:
            self.push_screen(ErrorScreen(missing_required))
            return

        platform_key = "macOS" if sys.platform == "darwin" else "Ubuntu"
        for dep in missing_optional:
            hint = dep.install_hint.get(platform_key, "")
            parts = [f"{dep.name} not found — {dep.feature} disabled"]
            if hint:
                parts.append(f"Install: {hint}")
            if dep.docs_url:
                parts.append(dep.docs_url)
            self.notify("  |  ".join(parts), severity="warning", timeout=15)

        self._refresh_branch()

    def action_help(self) -> None:
        from sdd_tui.tui.help import HelpScreen

        self.push_screen(HelpScreen())

    def action_skill_palette(self) -> None:
        from sdd_tui.tui.skill_palette import SkillPaletteScreen

        self.push_screen(SkillPaletteScreen())

    @property
    def changes(self) -> list[Change]:
        from sdd_tui.tui.epics import EpicsView

        return self.query_one(EpicsView)._changes

    def compose(self) -> ComposeResult:
        changes = self._load_changes()
        yield EpicsView(changes)

    def refresh_changes(self, include_archived: bool = False) -> list[Change]:
        self._refresh_branch()
        changes = self._load_changes(include_archived)
        self.query_one(EpicsView).update(changes)
        return changes

    def _refresh_branch(self) -> None:
        branch = self._git.get_branch(self._openspec_path.parent)
        self.sub_title = branch or ""

    def _load_changes(self, include_archived: bool = False) -> list[Change]:
        cwd = self._openspec_path.parent
        changes = load_all_changes(self._config, cwd, include_archived)
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
    from sdd_tui.core.config import load_config

    openspec_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "openspec"

    if not openspec_path.exists():
        print(f"Error: openspec/ not found at {openspec_path}", file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config()
        app = SddTuiApp(openspec_path, config)
        app.run()
    except OpenspecNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
