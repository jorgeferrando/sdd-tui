from pathlib import Path
from unittest.mock import MagicMock, patch

from sdd_tui.tui.app import SddTuiApp
from sdd_tui.tui.change_detail import ChangeDetailScreen
from sdd_tui.tui.spec_evolution import SpecEvolutionScreen


def _git_mock() -> MagicMock:
    m = MagicMock()
    m.return_value.is_clean.return_value = True
    m.return_value.find_commit.return_value = None
    return m


async def test_spec_evolution_default_delta_mode(openspec_with_change: Path) -> None:
    """REQ-16: SpecEvolutionScreen loads in delta mode by default."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            await pilot.press("e")
            assert isinstance(app.screen, SpecEvolutionScreen)
            assert "delta" in app.screen.title


async def test_spec_evolution_d_toggles_canonical(openspec_with_change: Path) -> None:
    """REQ-17: pressing 'D' toggles between delta and canonical mode."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            await pilot.press("e")
            assert "delta" in app.screen.title
            await pilot.press("d")
            assert "canonical" in app.screen.title
            await pilot.press("d")
            assert "delta" in app.screen.title


async def test_spec_evolution_esc_goes_back(openspec_with_change: Path) -> None:
    """REQ-18: pressing Esc pops back to ChangeDetailScreen."""
    with patch("sdd_tui.tui.app.GitReader", _git_mock()):
        app = SddTuiApp(openspec_with_change)
        async with app.run_test() as pilot:
            await pilot.press("enter")
            await pilot.press("e")
            assert isinstance(app.screen, SpecEvolutionScreen)
            await pilot.press("escape")
            assert isinstance(app.screen, ChangeDetailScreen)
