from __future__ import annotations

import os
import subprocess
from typing import Protocol


class Transport(Protocol):
    """Protocol for terminal multiplexer transports."""

    @property
    def name(self) -> str: ...

    def is_available(self) -> bool:
        """Returns True if this transport is active in the current environment."""
        ...

    def find_pane(self, process_name: str) -> str | None:
        """Find a pane running the given process. Returns pane ID or None."""
        ...

    def send_command(self, pane_id: str, command: str) -> None:
        """Send a command string followed by Enter to the given pane."""
        ...


class TmuxTransport:
    """Transport adapter for tmux.

    Detects via $TMUX. Targets panes by ID, so it can send to any pane
    regardless of which one is focused.
    """

    @property
    def name(self) -> str:
        return "tmux"

    def is_available(self) -> bool:
        return bool(os.environ.get("TMUX"))

    def find_pane(self, process_name: str) -> str | None:
        try:
            result = subprocess.run(
                ["tmux", "list-panes", "-a", "-F", "#{pane_id} #{pane_current_command}"],
                capture_output=True,
                text=True,
                check=True,
            )
            for line in result.stdout.strip().splitlines():
                parts = line.split(" ", 1)
                if len(parts) == 2 and process_name.lower() in parts[1].lower():
                    return parts[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def send_command(self, pane_id: str, command: str) -> None:
        subprocess.run(
            ["tmux", "send-keys", "-t", pane_id, command, "Enter"],
            check=True,
        )


class ZellijTransport:
    """Transport adapter for Zellij.

    Detects via $ZELLIJ. Limitation: Zellij's CLI sends to the focused pane
    only — there is no way to target a specific pane by process name.
    The pane_id parameter is ignored; the user must have the agent pane focused.
    """

    @property
    def name(self) -> str:
        return "zellij"

    def is_available(self) -> bool:
        return bool(os.environ.get("ZELLIJ"))

    def find_pane(self, process_name: str) -> str | None:
        # Zellij has no CLI to list/target panes by process name.
        # Returns "focused" as sentinel — the focused pane will receive input.
        return "focused" if self.is_available() else None

    def send_command(self, pane_id: str, command: str) -> None:
        subprocess.run(["zellij", "action", "write-chars", command], check=True)
        subprocess.run(["zellij", "action", "write", "10"], check=True)  # Enter


def detect_transport() -> Transport | None:
    """Auto-detect the active terminal multiplexer.

    Checks $TMUX then $ZELLIJ. Returns the first available transport,
    or None if no multiplexer is active.
    """
    for transport in [TmuxTransport(), ZellijTransport()]:
        if transport.is_available():
            return transport
    return None
