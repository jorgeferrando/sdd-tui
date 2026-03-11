from pathlib import Path

import pytest
from textual.widgets import Input, OptionList, Static
from textual.widgets.option_list import Option

from sdd_tui.tui.setup import _QUESTIONS, GitWorkflowSetupScreen

# Number of git-workflow-only questions (steps 1-5)
_GIT_QUESTIONS_COUNT = 5


def _make_screen(tmp_path: Path) -> GitWorkflowSetupScreen:
    openspec = tmp_path / "openspec"
    openspec.mkdir(exist_ok=True)
    return GitWorkflowSetupScreen(openspec)


def _select_option(screen: GitWorkflowSetupScreen, ol: OptionList, opt: Option, idx: int) -> None:
    event = OptionList.OptionSelected(ol, opt, idx)
    screen.on_option_list_option_selected(event)


# --- Step progression ---


@pytest.mark.asyncio
async def test_wizard_starts_at_step_1(tmp_path: Path) -> None:
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self) -> None:
            self.push_screen(_make_screen(tmp_path))

    async with TestApp().run_test() as pilot:
        screen = pilot.app.screen
        progress = screen.query_one("#wz-progress", Static)
        text = str(progress.render())
        assert "1" in text
        assert str(len(_QUESTIONS)) in text


@pytest.mark.asyncio
async def test_wizard_advances_on_option_selected(tmp_path: Path) -> None:
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self) -> None:
            self.push_screen(_make_screen(tmp_path))

    async with TestApp().run_test() as pilot:
        screen = pilot.app.screen
        ol = screen.query_one("#wz-options", OptionList)
        # Select first non-disabled option (index 0 = "github")
        first_opt = ol.get_option_at_index(0)
        _select_option(screen, ol, first_opt, 0)
        await pilot.pause()

        progress = screen.query_one("#wz-progress", Static)
        assert "2" in str(progress.render())


@pytest.mark.asyncio
async def test_disabled_option_does_not_advance(tmp_path: Path) -> None:
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self) -> None:
            self.push_screen(_make_screen(tmp_path))

    async with TestApp().run_test() as pilot:
        screen = pilot.app.screen
        ol = screen.query_one("#wz-options", OptionList)
        disabled_opt = Option("JIRA  (coming soon)", id="_disabled_jira")
        _select_option(screen, ol, disabled_opt, 1)
        await pilot.pause()

        # Step should still be 1
        progress = screen.query_one("#wz-progress", Static)
        assert "1" in str(progress.render())


@pytest.mark.asyncio
async def test_escape_cancels_without_writing(tmp_path: Path) -> None:
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self) -> None:
            self.push_screen(_make_screen(tmp_path))

    openspec = tmp_path / "openspec"
    async with TestApp().run_test() as pilot:
        await pilot.press("escape")
        await pilot.pause()

        assert not (openspec / "config.yaml").exists()


@pytest.mark.asyncio
async def test_completing_wizard_writes_config(tmp_path: Path) -> None:
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self) -> None:
            self.push_screen(_make_screen(tmp_path))

    openspec = tmp_path / "openspec"
    async with TestApp().run_test() as pilot:
        screen = pilot.app.screen

        for _ in range(len(_QUESTIONS)):
            ol = screen.query_one("#wz-options", OptionList)
            for idx in range(ol.option_count):
                opt = ol.get_option_at_index(idx)
                if not str(opt.id).startswith("_disabled_"):
                    _select_option(screen, ol, opt, idx)
                    await pilot.pause()
                    break

    assert (openspec / "config.yaml").exists()
    content = (openspec / "config.yaml").read_text()
    assert "git_workflow:" in content


@pytest.mark.asyncio
async def test_custom_prefix_shows_input(tmp_path: Path) -> None:
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self) -> None:
            self.push_screen(_make_screen(tmp_path))

    async with TestApp().run_test() as pilot:
        screen = pilot.app.screen

        # Advance to step 4 (change_prefix) by answering steps 1-3
        for _ in range(3):
            ol = screen.query_one("#wz-options", OptionList)
            for idx in range(ol.option_count):
                opt = ol.get_option_at_index(idx)
                if not str(opt.id).startswith("_disabled_"):
                    _select_option(screen, ol, opt, idx)
                    await pilot.pause()
                    break

        # Now on step 4 (change_prefix) — select "custom"
        ol = screen.query_one("#wz-options", OptionList)
        for idx in range(ol.option_count):
            opt = ol.get_option_at_index(idx)
            if str(opt.id) == "custom":
                _select_option(screen, ol, opt, idx)
                await pilot.pause()
                break

        custom_input = screen.query_one("#wz-custom", Input)
        assert custom_input.display is True


# --- Release workflow wizard steps ---


def _answer_git_steps(screen: GitWorkflowSetupScreen, ol_getter, pilot_pause) -> None:
    """Helper: answer all 5 git-workflow steps with the first non-disabled option."""

    async def _run():
        for _ in range(_GIT_QUESTIONS_COUNT):
            ol = screen.query_one("#wz-options", OptionList)
            for idx in range(ol.option_count):
                opt = ol.get_option_at_index(idx)
                if not str(opt.id).startswith("_disabled_"):
                    _select_option(screen, ol, opt, idx)
                    await pilot_pause()
                    break

    return _run()


@pytest.mark.asyncio
async def test_wizard_release_yes_shows_versioning_step(tmp_path: Path) -> None:
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self) -> None:
            self.push_screen(_make_screen(tmp_path))

    async with TestApp().run_test() as pilot:
        screen = pilot.app.screen

        # Answer git workflow steps (1-5)
        for _ in range(_GIT_QUESTIONS_COUNT):
            ol = screen.query_one("#wz-options", OptionList)
            for idx in range(ol.option_count):
                opt = ol.get_option_at_index(idx)
                if not str(opt.id).startswith("_disabled_"):
                    _select_option(screen, ol, opt, idx)
                    await pilot.pause()
                    break

        # Step 6: releases_enabled — select "yes"
        ol = screen.query_one("#wz-options", OptionList)
        for idx in range(ol.option_count):
            opt = ol.get_option_at_index(idx)
            if str(opt.id) == "yes":
                _select_option(screen, ol, opt, idx)
                await pilot.pause()
                break

        # Should now be on versioning step
        title = str(screen.query_one("#wz-title", Static).render())
        assert "versioning" in title.lower()


@pytest.mark.asyncio
async def test_wizard_release_no_skips_to_completion(tmp_path: Path) -> None:
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self) -> None:
            self.push_screen(_make_screen(tmp_path))

    openspec = tmp_path / "openspec"
    async with TestApp().run_test() as pilot:
        screen = pilot.app.screen

        # Answer git workflow steps (1-5)
        for _ in range(_GIT_QUESTIONS_COUNT):
            ol = screen.query_one("#wz-options", OptionList)
            for idx in range(ol.option_count):
                opt = ol.get_option_at_index(idx)
                if not str(opt.id).startswith("_disabled_"):
                    _select_option(screen, ol, opt, idx)
                    await pilot.pause()
                    break

        # Step 6: releases_enabled — select "no"
        ol = screen.query_one("#wz-options", OptionList)
        for idx in range(ol.option_count):
            opt = ol.get_option_at_index(idx)
            if str(opt.id) == "no":
                _select_option(screen, ol, opt, idx)
                await pilot.pause()
                break

        # Wizard should have completed — config.yaml written
        assert (openspec / "config.yaml").exists()
        content = (openspec / "config.yaml").read_text()
        assert "release_workflow:" in content
        assert "enabled: false" in content


@pytest.mark.asyncio
async def test_wizard_release_yes_writes_enabled_true(tmp_path: Path) -> None:
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            return iter([])

        def on_mount(self) -> None:
            self.push_screen(_make_screen(tmp_path))

    openspec = tmp_path / "openspec"
    # Pre-create config.yaml with project name for default formula path
    openspec.mkdir()
    (openspec / "config.yaml").write_text("project: my-project\n")

    async with TestApp().run_test() as pilot:
        screen = pilot.app.screen

        for _ in range(len(_QUESTIONS)):
            ol = screen.query_one("#wz-options", OptionList)
            for idx in range(ol.option_count):
                opt = ol.get_option_at_index(idx)
                if not str(opt.id).startswith("_disabled_"):
                    _select_option(screen, ol, opt, idx)
                    await pilot.pause()
                    break

    content = (openspec / "config.yaml").read_text()
    assert "release_workflow:" in content
    assert "enabled: true" in content


@pytest.mark.asyncio
async def test_on_mount_notifies_when_release_workflow_absent(tmp_path: Path) -> None:

    from sdd_tui.tui.app import SddTuiApp

    openspec = tmp_path / "openspec"
    openspec.mkdir()
    (openspec / "config.yaml").write_text("project: test\n")
    (openspec / "changes").mkdir()

    notifications: list[str] = []

    class PatchedApp(SddTuiApp):
        def notify(self, message: str, **kwargs) -> None:  # type: ignore[override]
            notifications.append(message)

    async with PatchedApp(openspec).run_test() as pilot:
        await pilot.pause()

    assert any("Release workflow" in n for n in notifications)


@pytest.mark.asyncio
async def test_on_mount_no_notify_when_release_workflow_disabled(tmp_path: Path) -> None:
    from sdd_tui.tui.app import SddTuiApp

    openspec = tmp_path / "openspec"
    openspec.mkdir()
    (openspec / "config.yaml").write_text(
        "project: test\n"
        "release_workflow:\n"
        "  enabled: false\n"
        "  versioning: semver\n"
        "  changelog_source: openspec\n"
        "  homebrew_formula: null\n"
    )
    (openspec / "changes").mkdir()

    release_notifications: list[str] = []

    class PatchedApp(SddTuiApp):
        def notify(self, message: str, **kwargs) -> None:  # type: ignore[override]
            if "Release workflow" in message:
                release_notifications.append(message)

    async with PatchedApp(openspec).run_test() as pilot:
        await pilot.pause()

    assert len(release_notifications) == 0
