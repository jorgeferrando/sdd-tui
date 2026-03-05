from __future__ import annotations

from unittest.mock import MagicMock, patch

from sdd_tui.core.deps import Dep, _is_present, check_deps


def _make_dep(required: bool = True) -> Dep:
    return Dep(
        name="test-tool",
        required=required,
        check_cmd=["test-tool", "--version"],
        install_hint={"macOS": "brew install test-tool"},
        docs_url="https://example.com",
        feature=None if required else "some-feature",
    )


def _mock_run(returncode: int) -> MagicMock:
    result = MagicMock()
    result.returncode = returncode
    return result


# --- _is_present ---


def test_is_present_returns_true_when_returncode_zero() -> None:
    dep = _make_dep()
    with patch("sdd_tui.core.deps.subprocess.run", return_value=_mock_run(0)):
        assert _is_present(dep) is True


def test_is_present_returns_false_when_returncode_nonzero() -> None:
    dep = _make_dep()
    with patch("sdd_tui.core.deps.subprocess.run", return_value=_mock_run(1)):
        assert _is_present(dep) is False


def test_is_present_returns_false_on_file_not_found() -> None:
    dep = _make_dep()
    with patch("sdd_tui.core.deps.subprocess.run", side_effect=FileNotFoundError):
        assert _is_present(dep) is False


# --- check_deps ---


def test_check_deps_returns_empty_when_all_present() -> None:
    with patch("sdd_tui.core.deps._is_present", return_value=True):
        missing_req, missing_opt = check_deps()
    assert missing_req == []
    assert missing_opt == []


def test_check_deps_separates_required_and_optional() -> None:
    from sdd_tui.core.deps import DEPS

    def fake_is_present(dep: Dep) -> bool:
        return False

    with patch("sdd_tui.core.deps._is_present", side_effect=fake_is_present):
        missing_req, missing_opt = check_deps()

    required_names = {d.name for d in DEPS if d.required}
    optional_names = {d.name for d in DEPS if not d.required}

    assert {d.name for d in missing_req} == required_names
    assert {d.name for d in missing_opt} == optional_names


def test_check_deps_required_missing_file_not_found() -> None:
    from sdd_tui.core.deps import DEPS

    required_dep = next(d for d in DEPS if d.required)

    def fake_is_present(dep: Dep) -> bool:
        return dep.name != required_dep.name

    with patch("sdd_tui.core.deps._is_present", side_effect=fake_is_present):
        missing_req, missing_opt = check_deps()

    assert any(d.name == required_dep.name for d in missing_req)
    assert not any(d.name == required_dep.name for d in missing_opt)


def test_check_deps_optional_missing() -> None:
    from sdd_tui.core.deps import DEPS

    optional_dep = next(d for d in DEPS if not d.required)

    def fake_is_present(dep: Dep) -> bool:
        return dep.name != optional_dep.name

    with patch("sdd_tui.core.deps._is_present", side_effect=fake_is_present):
        missing_req, missing_opt = check_deps()

    assert missing_req == []
    assert any(d.name == optional_dep.name for d in missing_opt)


def test_check_deps_checks_are_independent() -> None:
    """Fallo de un dep no impide comprobar el resto."""
    call_count = 0

    def fake_is_present(dep: Dep) -> bool:
        nonlocal call_count
        call_count += 1
        return False

    from sdd_tui.core.deps import DEPS

    with patch("sdd_tui.core.deps._is_present", side_effect=fake_is_present):
        check_deps()

    assert call_count == len(DEPS)
