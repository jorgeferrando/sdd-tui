from __future__ import annotations

from pathlib import Path

from rich.syntax import Syntax
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import DataTable, Footer, Header, Static

from sdd_tui.core.git_reader import GitReader
from sdd_tui.core.github import CiStatus, PrStatus
from sdd_tui.core.metrics import ChangeMetrics, parse_metrics
from sdd_tui.core.models import Change, PhaseState, Pipeline, Task, TaskGitState
from sdd_tui.tui.doc_viewer import DocumentViewerScreen, SpecSelectorScreen
from sdd_tui.tui.spec_evolution import SpecEvolutionScreen

DONE = "✓"
PENDING = "·"
PHASES = ["propose", "spec", "design", "tasks", "apply", "verify"]

_PR_LOADING = object()  # sentinel: worker not yet finished
_CI_LOADING = object()  # sentinel: worker not yet finished
_PR_STATE_SYMBOL: dict[str, str] = {"OPEN": "⧗", "MERGED": DONE, "CLOSED": "✗"}


class TaskListPanel(Widget):
    DEFAULT_CSS = """
    TaskListPanel {
        width: 2fr;
    }
    """

    def __init__(self, tasks: list[Task]) -> None:
        super().__init__()
        self._tasks = tasks
        self._row_task_map: dict[str, Task] = {}

    def compose(self) -> ComposeResult:
        yield DataTable(cursor_type="row", show_header=False)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("state", "hash", "id", "desc")

        if not self._tasks:
            table.add_row("", "", "", "No tasks defined yet")
            self.styles.height = 3
            return

        last_amendment: str | None = None
        row_count = 0
        for task in self._tasks:
            if task.amendment != last_amendment and task.amendment is not None:
                table.add_row("", f"── amendment: {task.amendment} ──", "", "")
                last_amendment = task.amendment
                row_count += 1

            state = DONE if task.git_state == TaskGitState.COMMITTED else PENDING
            hash_str = task.commit.hash if task.commit else " " * 7
            table.add_row(state, hash_str, task.id, task.description, key=task.id)
            self._row_task_map[task.id] = task
            row_count += 1

        self._row_count = row_count
        self.call_after_refresh(self._set_height)

    def _set_height(self) -> None:
        screen_h = self.app.size.height
        max_list_height = max(6, screen_h - 10)
        self.styles.height = min(self._row_count + 1, max_list_height)

    def get_task(self, row_key: str) -> Task | None:
        return self._row_task_map.get(row_key)


class PipelinePanel(Static):
    DEFAULT_CSS = """
    PipelinePanel {
        width: 1fr;
        height: auto;
        padding: 1 2;
        border-left: solid $panel-darken-2;
    }
    """

    def __init__(
        self,
        pipeline: Pipeline,
        tasks: list[Task],
        metrics: ChangeMetrics | None = None,
        pr_status: PrStatus | None | object = _PR_LOADING,
        ci_status: CiStatus | None | object = _CI_LOADING,
    ) -> None:
        self._pipeline = pipeline
        self._tasks = tasks
        self._metrics = metrics
        self._pr_status: PrStatus | None | object = pr_status
        self._ci_status: CiStatus | None | object = ci_status
        self._text = self._build_content(pipeline, tasks, metrics, pr_status, ci_status)
        super().__init__(self._text)

    def update_pr(self, pr_status: PrStatus | None) -> None:
        self._pr_status = pr_status
        self._text = self._build_content(
            self._pipeline, self._tasks, self._metrics, pr_status, self._ci_status
        )
        self.update(self._text)

    def update_ci(self, ci_status: CiStatus | None) -> None:
        self._ci_status = ci_status
        self._text = self._build_content(
            self._pipeline, self._tasks, self._metrics, self._pr_status, ci_status
        )
        self.update(self._text)

    def _build_content(
        self,
        pipeline: Pipeline,
        tasks: list[Task],
        metrics: ChangeMetrics | None,
        pr_status: PrStatus | None | object = _PR_LOADING,
        ci_status: CiStatus | None | object = _CI_LOADING,
    ) -> str:
        lines = ["PIPELINE", ""]
        for phase in PHASES:
            state = getattr(pipeline, phase)
            if phase == "apply" and state != PhaseState.DONE and tasks:
                done = sum(1 for t in tasks if t.done)
                symbol = f"{done}/{len(tasks)}" if done > 0 else PENDING
            else:
                symbol = DONE if state == PhaseState.DONE else PENDING
            lines.append(f"  {symbol:<3}  {phase}")
        if metrics is not None:
            lines.append("")
            if metrics.req_count == 0:
                lines.append("  REQ: —")
            else:
                pct = round(metrics.ears_count / metrics.req_count * 100)
                lines.append(f"  REQ: {metrics.req_count} ({pct}%)")
        lines.append("")
        lines.append(self._build_pr_line(pr_status))
        lines.append(self._build_ci_line(ci_status))
        return "\n".join(lines)

    def _build_pr_line(self, pr_status: PrStatus | None | object) -> str:
        if pr_status is _PR_LOADING:
            return "  …    PR"
        if pr_status is None:
            return "  —    PR"
        assert isinstance(pr_status, PrStatus)
        symbol = _PR_STATE_SYMBOL.get(pr_status.state, "?")
        parts = [f"  {symbol:<3}  PR #{pr_status.number}"]
        review_parts = []
        if pr_status.approvals > 0:
            review_parts.append(f"{pr_status.approvals}✓")
        if pr_status.changes_requested > 0:
            review_parts.append(f"{pr_status.changes_requested}✗")
        if review_parts:
            parts.append("  " + " ".join(review_parts))
        return "".join(parts)

    def _build_ci_line(self, ci_status: CiStatus | None | object) -> str:
        if ci_status is _CI_LOADING:
            return "  …    CI"
        if ci_status is None:
            return "  —    CI"
        assert isinstance(ci_status, CiStatus)
        if ci_status.status != "completed":
            return "  ⟳    CI"
        if ci_status.conclusion == "success":
            return "  ✓    CI"
        return "  ✗    CI"


class DiffPanel(ScrollableContainer):
    DEFAULT_CSS = """
    DiffPanel {
        height: 1fr;
        padding: 1 2;
        border-top: solid $panel-darken-2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Select a task to view its diff", id="diff-content")

    def show_diff(self, text: str) -> None:
        content = Syntax(text, "diff", theme="monokai", word_wrap=False)
        self.query_one("#diff-content", Static).update(content)
        self.scroll_home(animate=False)

    def show_message(self, text: str) -> None:
        self.query_one("#diff-content", Static).update(text)
        self.scroll_home(animate=False)


class ChangeDetailScreen(Screen):
    DEFAULT_CSS = """
    ChangeDetailScreen .top-panel {
        height: auto;
        min-height: 6;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh_view", "Refresh"),
        Binding("p", "view_proposal", "Proposal"),
        Binding("d", "view_design", "Design"),
        Binding("s", "view_spec", "Spec"),
        Binding("t", "view_tasks", "Tasks"),
        Binding("q", "view_requirements", "Requirements"),
        Binding("space", "copy_next_command", "Copy cmd", priority=True),
        Binding("e", "spec_evolution", "Spec evolution"),
        Binding("g", "git_log", "Git log"),
        Binding("shift+w", "ship_pr", "Ship PR"),
        Binding("K", "skill_palette", "Skills"),
    ]

    def __init__(self, change: Change) -> None:
        super().__init__()
        self._change = change
        self._metrics = parse_metrics(change.path, Path.cwd())

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            with Horizontal(classes="top-panel"):
                yield TaskListPanel(self._change.tasks)
                yield PipelinePanel(self._change.pipeline, self._change.tasks, self._metrics)
            yield DiffPanel()
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"sdd-tui — {self._change.name}"
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())
        self._load_pr_status_worker()
        self._load_ci_status_worker()

    @work(thread=True)
    def _load_pr_status_worker(self) -> None:
        from sdd_tui.core.github import get_pr_status

        pr_status = get_pr_status(self._change.name, self._change.project_path)
        self.app.call_from_thread(lambda s=pr_status: self.query_one(PipelinePanel).update_pr(s))

    @work(thread=True)
    def _load_ci_status_worker(self) -> None:
        from sdd_tui.core.github import get_ci_status

        cwd = self._change.project_path or Path.cwd()
        branch = GitReader().get_branch(cwd)
        ci_status = get_ci_status(branch, cwd) if branch else None
        self.app.call_from_thread(lambda s=ci_status: self.query_one(PipelinePanel).update_ci(s))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None or event.row_key.value is None:
            return
        task = self.query_one(TaskListPanel).get_task(event.row_key.value)
        if task is None:
            return
        try:
            diff_panel = self.query_one(DiffPanel)
        except Exception:
            return
        diff_panel.show_message("[dim]Loading diff…[/dim]")
        self._load_diff_worker(task)

    @work(thread=True, exclusive=True)
    def _load_diff_worker(self, task: Task) -> None:
        if task.git_state == TaskGitState.COMMITTED and task.commit:
            diff = GitReader().get_diff(task.commit.hash, Path.cwd())
            if diff:
                self.app.call_from_thread(self._update_diff_panel, diff, True)
            else:
                self.app.call_from_thread(self._update_diff_panel, "Could not load diff", False)
        else:
            diff = GitReader().get_working_diff(Path.cwd())
            if diff:
                status = GitReader().get_status_short(Path.cwd())
                if status:
                    header = (
                        "# Modified files:\n"
                        + "\n".join(f"# {line}" for line in status.splitlines())
                        + "\n#\n"
                    )
                else:
                    header = "# Staged changes:\n#\n"
                self.app.call_from_thread(self._update_diff_panel, header + diff, True)
            else:
                self.app.call_from_thread(self._update_diff_panel, "No uncommitted changes", False)

    def _update_diff_panel(self, text: str, as_diff: bool) -> None:
        try:
            diff_panel = self.query_one(DiffPanel)
        except Exception:
            return
        if as_diff:
            diff_panel.show_diff(text)
        else:
            diff_panel.show_message(text)

    def action_refresh_view(self) -> None:
        changes = self.app.refresh_changes()  # type: ignore[attr-defined]
        fresh_change = next((c for c in changes if c.name == self._change.name), None)
        if fresh_change is None:
            self.notify("Change not found — returning to list")
            self.app.pop_screen()
            return
        self._change = fresh_change
        self._metrics = parse_metrics(self._change.path, Path.cwd())
        top = self.query_one(".top-panel", Horizontal)
        self.query_one(TaskListPanel).remove()
        self.query_one(PipelinePanel).remove()
        top.mount(
            TaskListPanel(self._change.tasks),
            PipelinePanel(self._change.pipeline, self._change.tasks, self._metrics),
        )
        self.query_one(DiffPanel).show_message("Select a task to view its diff")
        self.call_after_refresh(lambda: self.query_one(DataTable).focus())

    def action_view_requirements(self) -> None:
        self._open_doc("requirements.md", "requirements")

    def action_view_proposal(self) -> None:
        self._open_doc("proposal.md", "proposal")

    def action_view_design(self) -> None:
        self._open_doc("design.md", "design")

    def action_view_tasks(self) -> None:
        self._open_doc("tasks.md", "tasks")

    def action_view_spec(self) -> None:
        specs_dir = self._change.path / "specs"
        domains = (
            sorted(d.name for d in specs_dir.iterdir() if d.is_dir() and (d / "spec.md").exists())
            if specs_dir.exists()
            else []
        )
        if not domains:
            self.notify("No specs found")
        elif len(domains) == 1:
            path = specs_dir / domains[0] / "spec.md"
            title = f"sdd-tui — {self._change.name} / spec:{domains[0]}"
            if path.exists():
                self.notify("Opening spec")
            self.app.push_screen(DocumentViewerScreen(path, title))
        else:
            self.app.push_screen(SpecSelectorScreen(self._change))

    def action_spec_evolution(self) -> None:
        self.app.push_screen(SpecEvolutionScreen(self._change))

    def action_git_log(self) -> None:
        from sdd_tui.tui.git_log import GitLogScreen

        self.app.push_screen(GitLogScreen(self._change))

    def action_skill_palette(self) -> None:
        from sdd_tui.tui.skill_palette import SkillPaletteScreen

        self.app.push_screen(SkillPaletteScreen(change_name=self._change.name))

    def action_ship_pr(self) -> None:
        desc = self._extract_proposal_description()
        title = f"[{self._change.name}] {desc}".strip() if desc else f"[{self._change.name}]"
        cmd = f'gh pr create --title "{title}" --body ""'
        self.app.copy_to_clipboard(cmd)
        self.notify(f"Copied: {cmd}")

    def _extract_proposal_description(self) -> str:
        proposal = self._change.path / "proposal.md"
        if not proposal.exists():
            return ""
        in_desc = False
        for line in proposal.read_text().splitlines():
            if line.startswith("## Descripción"):
                in_desc = True
                continue
            if in_desc:
                if line.startswith("##"):
                    break
                stripped = line.strip()
                if stripped:
                    return stripped
        return ""

    def _open_doc(self, filename: str, label: str) -> None:
        path = self._change.path / filename
        title = f"sdd-tui — {self._change.name} / {label}"
        if path.exists():
            self.notify(f"Opening {label}")
        self.app.push_screen(DocumentViewerScreen(path, title))

    def action_copy_next_command(self) -> None:
        cmd = self._build_next_command()
        self.app.copy_to_clipboard(cmd)
        self.notify(f"Copied: {cmd}")

    def _build_next_command(self) -> str:
        p = self._change.pipeline
        name = self._change.name
        if p.propose == PhaseState.PENDING:
            return f'/sdd-propose "{name}"'
        if p.spec == PhaseState.PENDING:
            return f"/sdd-spec {name}"
        if p.design == PhaseState.PENDING:
            return f"/sdd-design {name}"
        if p.tasks == PhaseState.PENDING:
            return f"/sdd-tasks {name}"
        if p.apply == PhaseState.PENDING:
            next_task = next((t for t in self._change.tasks if not t.done), None)
            if next_task:
                return f"/sdd-apply {next_task.id}"
            return f"/sdd-apply {name}"
        if p.verify == PhaseState.PENDING:
            return f"/sdd-verify {name}"
        return f"/sdd-archive {name}"
