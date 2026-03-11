from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Input, OptionList, Static
from textual.widgets.option_list import Option

from sdd_tui.core.providers.protocol import GitWorkflowConfig
from sdd_tui.core.reader import _write_git_workflow_config

_QUESTIONS: list[dict] = [
    {
        "key": "issue_tracker",
        "title": "Where do you manage issues?",
        "options": [
            ("github", "GitHub Issues"),
            ("_disabled_jira", "JIRA  (coming soon)"),
            ("_disabled_trello", "Trello  (coming soon)"),
            ("none", "No issue tracker"),
        ],
    },
    {
        "key": "git_host",
        "title": "Where is your git repository hosted?",
        "options": [
            ("github", "GitHub"),
            ("_disabled_gitlab", "GitLab  (coming soon)"),
            ("_disabled_bitbucket", "Bitbucket  (coming soon)"),
            ("none", "Other / self-hosted"),
        ],
    },
    {
        "key": "branching_model",
        "title": "Which branching model do you use?",
        "options": [
            ("github-flow", "GitHub Flow  (main + feature branches)"),
            ("_disabled_git-flow", "Git Flow  (coming soon)"),
        ],
    },
    {
        "key": "change_prefix",
        "title": "What prefix do you use for change branches?",
        "options": [
            ("issue", "issue  (e.g. issue-42-fix-bug)"),
            ("feature", "feature  (e.g. feature/add-auth)"),
            ("custom", "Custom prefix…"),
        ],
    },
    {
        "key": "changelog_format",
        "title": "How do you generate your changelog?",
        "options": [
            ("both", "Both labels and commit prefixes"),
            ("labels", "Labels only"),
            ("commit-prefix", "Commit prefix only  (feat:, fix:, …)"),
        ],
    },
]


class GitWorkflowSetupScreen(Screen):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    CSS = """
    GitWorkflowSetupScreen {
        align: center middle;
    }
    #wz-container {
        width: 70;
        height: auto;
        border: solid $primary;
        padding: 1 2;
    }
    #wz-progress {
        color: $text-muted;
        margin-bottom: 1;
    }
    #wz-title {
        text-style: bold;
        margin-bottom: 1;
    }
    #wz-custom {
        margin-top: 1;
        display: none;
    }
    """

    def __init__(self, openspec_path: Path) -> None:
        super().__init__()
        self._openspec_path = openspec_path
        self._step: int = 0
        self._answers: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        from textual.containers import Vertical

        with Vertical(id="wz-container"):
            yield Static("", id="wz-progress")
            yield Static("", id="wz-title")
            yield OptionList(id="wz-options")
            yield Input(id="wz-custom", placeholder="Type the prefix…")

    def on_mount(self) -> None:
        self._render_step()

    def _render_step(self) -> None:
        q = _QUESTIONS[self._step]
        total = len(_QUESTIONS)
        self.query_one("#wz-progress", Static).update(f"Step {self._step + 1} of {total}")
        self.query_one("#wz-title", Static).update(q["title"])

        ol = self.query_one("#wz-options", OptionList)
        ol.clear_options()
        for opt_id, opt_label in q["options"]:
            if opt_id.startswith("_disabled_"):
                ol.add_option(Option(opt_label, id=opt_id, disabled=True))
            else:
                ol.add_option(Option(opt_label, id=opt_id))

        # Hide custom input when rendering a new step
        custom = self.query_one("#wz-custom", Input)
        custom.display = False
        custom.value = ""

        self.call_after_refresh(lambda: ol.focus())

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        opt_id = str(event.option.id)
        if opt_id.startswith("_disabled_"):
            self.notify("Not yet available", severity="warning")
            return
        if opt_id == "custom":
            custom = self.query_one("#wz-custom", Input)
            custom.display = True
            custom.focus()
            return
        self._record_answer(opt_id)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if value:
            self._record_answer(value)

    def _record_answer(self, value: str) -> None:
        key = _QUESTIONS[self._step]["key"]
        self._answers[key] = value
        self._step += 1
        if self._step == len(_QUESTIONS):
            self._save_and_dismiss()
        else:
            self._render_step()

    def _save_and_dismiss(self) -> None:
        cfg = GitWorkflowConfig(**self._answers)
        _write_git_workflow_config(self._openspec_path, cfg)
        self.app.notify("Git workflow configured ✓")
        self.app.pop_screen()

    def action_cancel(self) -> None:
        self.app.pop_screen()
