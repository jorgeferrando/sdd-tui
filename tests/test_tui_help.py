from pathlib import Path
from unittest.mock import MagicMock, patch

from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.help import HELP_CONTENT, HelpScreen


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


def test_help_screen_jk_bindings() -> None:
    """REQ-06: HelpScreen exposes j/k scroll bindings."""
    keys = {b.key for b in HelpScreen.BINDINGS}
    assert "j" in keys
    assert "k" in keys


def test_help_content_has_all_sections() -> None:
    """REQ-04/05: HELP_CONTENT contains all six expected sections."""
    text = str(HELP_CONTENT)
    assert "VIEW 1" in text
    assert "VIEW 2" in text
    assert "VIEW 8" in text
    assert "VIEW 9" in text
    assert "VIEWERS" in text
    assert "GLOBAL" in text


async def test_help_screen_opens_on_question_mark(openspec_with_change: Path) -> None:
    """REQ-01/02: pressing ? from View 1 opens HelpScreen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("question_mark")
            assert isinstance(app.screen, HelpScreen)


async def test_help_screen_esc_closes(openspec_with_change: Path) -> None:
    """REQ-03: pressing Esc in HelpScreen pops back to the previous screen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("question_mark")
            assert isinstance(app.screen, HelpScreen)
            await pilot.press("escape")
            assert not isinstance(app.screen, HelpScreen)
            assert len(app.screen_stack) == 1
