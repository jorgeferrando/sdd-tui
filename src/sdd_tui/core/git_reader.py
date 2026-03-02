from __future__ import annotations

import subprocess
from pathlib import Path


class GitReader:
    def is_clean(self, cwd: Path) -> bool | None:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return None
            return result.stdout.strip() == ""
        except FileNotFoundError:
            return None
