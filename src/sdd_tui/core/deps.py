from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass
class Dep:
    name: str
    required: bool
    check_cmd: list[str]
    install_hint: dict[str, str]
    docs_url: str | None
    feature: str | None


DEPS: list[Dep] = [
    Dep(
        name="git",
        required=True,
        check_cmd=["git", "--version"],
        install_hint={
            "macOS": "brew install git",
            "Ubuntu": "sudo apt install git",
        },
        docs_url="https://git-scm.com/downloads",
        feature=None,
    ),
    Dep(
        name="gh",
        required=False,
        check_cmd=["gh", "--version"],
        install_hint={
            "macOS": "brew install gh",
            "Ubuntu": "sudo apt install gh",
        },
        docs_url="https://cli.github.com",
        feature="pr-status",
    ),
]


def check_deps() -> tuple[list[Dep], list[Dep]]:
    """Returns (missing_required, missing_optional)."""
    missing_required: list[Dep] = []
    missing_optional: list[Dep] = []
    for dep in DEPS:
        if not _is_present(dep):
            if dep.required:
                missing_required.append(dep)
            else:
                missing_optional.append(dep)
    return missing_required, missing_optional


def _is_present(dep: Dep) -> bool:
    try:
        result = subprocess.run(dep.check_cmd, capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False
