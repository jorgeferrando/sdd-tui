from pathlib import Path
from unittest.mock import MagicMock, patch

from textual.widgets import DataTable

from sdd_tui.core.skills import SkillInfo
from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.skill_palette import SkillPaletteScreen


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


def _two_skills() -> list[SkillInfo]:
    return [
        SkillInfo(name="sdd-apply", description="SDD Apply - implementation"),
        SkillInfo(name="build", description="Vertical BUILD - code"),
    ]


async def test_skill_palette_mounts_without_crash(
    openspec_with_change: Path,
) -> None:
    """REQ-01: SkillPaletteScreen mounts and shows a DataTable."""
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.skill_palette.load_skills", return_value=_two_skills()),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("K")
            assert isinstance(app.screen, SkillPaletteScreen)
            table = app.screen.query_one(DataTable)
            assert table.row_count == 2


async def test_skill_palette_shows_no_skills_when_empty(
    openspec_with_change: Path,
) -> None:
    """REQ-02: no skills → 'No skills found' message."""
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.skill_palette.load_skills", return_value=[]),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("K")
            assert isinstance(app.screen, SkillPaletteScreen)
            table = app.screen.query_one(DataTable)
            assert table.row_count == 1
            row = table.get_row_at(0)
            assert any("No skills found" in str(cell) for cell in row)


async def test_enter_copies_command_without_context(
    openspec_with_change: Path,
) -> None:
    """REQ-11: without change_name, Enter copies /skill-name."""
    copied: list[str] = []

    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.skill_palette.load_skills", return_value=_two_skills()),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("K")
            assert isinstance(app.screen, SkillPaletteScreen)
            app.screen.app.copy_to_clipboard = lambda text: copied.append(text)  # type: ignore[method-assign]
            await pilot.press("enter")
            assert copied == ["/sdd-apply"]


async def test_enter_copies_command_with_context_aware_skill(
    openspec_with_change: Path,
) -> None:
    """REQ-10: with change_name and context-aware skill, Enter copies /skill change."""
    copied: list[str] = []

    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.skill_palette.load_skills", return_value=_two_skills()),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            # Open from ChangeDetailScreen context by pushing directly
            palette = SkillPaletteScreen(change_name="my-feature")
            await app.push_screen(palette)
            await pilot.pause()
            assert isinstance(app.screen, SkillPaletteScreen)
            app.screen.app.copy_to_clipboard = lambda text: copied.append(text)  # type: ignore[method-assign]
            await pilot.press("enter")
            assert copied == ["/sdd-apply my-feature"]


async def test_enter_copies_command_with_non_context_aware_skill(
    openspec_with_change: Path,
) -> None:
    """REQ-11: with change_name but non-context-aware skill, Enter copies /skill without change."""
    copied: list[str] = []
    non_context_skills = [
        SkillInfo(name="sdd-new", description="SDD New - start a change"),
    ]

    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.skill_palette.load_skills", return_value=non_context_skills),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            palette = SkillPaletteScreen(change_name="my-feature")
            await app.push_screen(palette)
            await pilot.pause()
            app.screen.app.copy_to_clipboard = lambda text: copied.append(text)  # type: ignore[method-assign]
            await pilot.press("enter")
            assert copied == ["/sdd-new"]


async def test_filter_reduces_rows(openspec_with_change: Path) -> None:
    """REQ-05: filter input reduces visible rows."""
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.skill_palette.load_skills", return_value=_two_skills()),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("K")
            assert isinstance(app.screen, SkillPaletteScreen)
            table = app.screen.query_one(DataTable)
            assert table.row_count == 2

            # Activate filter
            screen: SkillPaletteScreen = app.screen
            screen._search_query = "sdd"
            screen._populate()
            await pilot.pause()
            assert table.row_count == 1


async def test_esc_clears_filter_before_pop(openspec_with_change: Path) -> None:
    """REQ-06/07: first Esc clears filter without closing screen, second Esc pops."""
    with (
        patch("sdd_tui.tui.app.GitReader", _git_mock()),
        patch("sdd_tui.tui.skill_palette.load_skills", return_value=_two_skills()),
    ):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("K")
            assert isinstance(app.screen, SkillPaletteScreen)
            screen: SkillPaletteScreen = app.screen

            # Activate search mode manually
            screen._search_mode = True
            screen._search_query = "sdd"
            search_input = screen.query_one("#search-input")
            search_input.display = True

            # First Esc: should clear filter, NOT pop screen
            await pilot.press("escape")
            assert isinstance(app.screen, SkillPaletteScreen)
            assert screen._search_query == ""
            assert screen._search_mode is False

            # Second Esc: should pop screen (back to EpicsView)
            await pilot.press("escape")
            assert not isinstance(app.screen, SkillPaletteScreen)
