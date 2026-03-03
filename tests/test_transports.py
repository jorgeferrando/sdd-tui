from unittest.mock import patch

import pytest

from sdd_tui.core.transports import (
    TmuxTransport,
    ZellijTransport,
    detect_transport,
)


# ── TmuxTransport ──────────────────────────────────────────────────────────────

def test_tmux_available_when_env_set():
    with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,1234,0"}):
        assert TmuxTransport().is_available() is True


def test_tmux_not_available_when_env_missing():
    with patch.dict("os.environ", {}, clear=True):
        assert TmuxTransport().is_available() is False


def test_tmux_find_pane_returns_id_when_found():
    output = "%0 zsh\n%1 claude\n%2 python\n"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = output
        mock_run.return_value.returncode = 0
        result = TmuxTransport().find_pane("claude")
    assert result == "%1"


def test_tmux_find_pane_returns_none_when_not_found():
    output = "%0 zsh\n%1 python\n"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = output
        mock_run.return_value.returncode = 0
        result = TmuxTransport().find_pane("claude")
    assert result is None


def test_tmux_find_pane_returns_none_on_error():
    import subprocess
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = TmuxTransport().find_pane("claude")
    assert result is None


def test_tmux_send_command_calls_send_keys():
    with patch("subprocess.run") as mock_run:
        TmuxTransport().send_command("%1", "/sdd:apply T01")
    mock_run.assert_called_once_with(
        ["tmux", "send-keys", "-t", "%1", "/sdd:apply T01", "Enter"],
        check=True,
    )


def test_tmux_name():
    assert TmuxTransport().name == "tmux"


# ── ZellijTransport ────────────────────────────────────────────────────────────

def test_zellij_available_when_env_set():
    with patch.dict("os.environ", {"ZELLIJ": "0"}):
        assert ZellijTransport().is_available() is True


def test_zellij_not_available_when_env_missing():
    with patch.dict("os.environ", {}, clear=True):
        assert ZellijTransport().is_available() is False


def test_zellij_find_pane_returns_none_targeting_unsupported():
    with patch.dict("os.environ", {"ZELLIJ": "0"}):
        result = ZellijTransport().find_pane("claude")
    assert result is None


def test_zellij_find_pane_returns_none_when_unavailable():
    with patch.dict("os.environ", {}, clear=True):
        result = ZellijTransport().find_pane("claude")
    assert result is None


def test_zellij_send_command_calls_write_chars_and_enter():
    calls = []
    with patch("subprocess.run", side_effect=lambda args, **_: calls.append(args)):
        ZellijTransport().send_command("focused", "/sdd:apply T01")
    assert calls[0] == ["zellij", "action", "write-chars", "/sdd:apply T01"]
    assert calls[1] == ["zellij", "action", "write", "10"]


def test_zellij_name():
    assert ZellijTransport().name == "zellij"


# ── detect_transport ───────────────────────────────────────────────────────────

def test_detect_returns_tmux_when_tmux_active():
    with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default", "ZELLIJ": ""}):
        transport = detect_transport()
    assert transport is not None
    assert transport.name == "tmux"


def test_detect_returns_zellij_when_only_zellij_active():
    with patch.dict("os.environ", {"ZELLIJ": "0"}, clear=True):
        transport = detect_transport()
    assert transport is not None
    assert transport.name == "zellij"


def test_detect_returns_none_when_no_multiplexer():
    with patch.dict("os.environ", {}, clear=True):
        transport = detect_transport()
    assert transport is None
