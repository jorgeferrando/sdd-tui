from __future__ import annotations

import subprocess
from pathlib import Path

from sdd_tui.core.models import CommitInfo


class GitReader:
    def find_commit(self, message_fragment: str | None, cwd: Path) -> CommitInfo | None:
        if message_fragment is None:
            return None
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--abbrev-commit", "-F",
                 f"--grep={message_fragment}", "-1"],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0 or not result.stdout.strip():
                return None
            parts = result.stdout.strip().split(" ", 1)
            if len(parts) < 2:
                return None
            return CommitInfo(hash=parts[0], message=parts[1])
        except FileNotFoundError:
            return None

    def get_diff(self, commit_hash: str | None, cwd: Path) -> str | None:
        if not commit_hash:
            return None
        try:
            result = subprocess.run(
                ["git", "show", "--no-color", commit_hash],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return None
            return result.stdout
        except FileNotFoundError:
            return None

    def get_working_diff(self, cwd: Path) -> str | None:
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD", "--no-color"],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return None
            return result.stdout or None
        except FileNotFoundError:
            return None

    def is_clean(self, cwd: Path) -> bool | None:
        try:
            toplevel = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            if toplevel.returncode != 0:
                return None
            root = Path(toplevel.stdout.strip())
            result = subprocess.run(
                ["git", "status", "--porcelain", "--", ".", ":(exclude)openspec/", ":(exclude).claude/"],
                cwd=root,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return None
            return result.stdout.strip() == ""
        except FileNotFoundError:
            return None
