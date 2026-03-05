"""sdd-setup — installs SDD skills from GitHub into Claude Code skills directory."""

from __future__ import annotations

import argparse
import importlib.metadata
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GITHUB_REPO = "https://github.com/jorgeferrando/sdd-tui"
SKILLS_PREFIX = "sdd-"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sdd-setup",
        description="Install SDD skills for Claude Code from GitHub.",
    )
    dest_group = parser.add_mutually_exclusive_group()
    dest_group.add_argument(
        "--global",
        dest="global_",
        action="store_true",
        help="Install into ~/.claude/skills/ (available in all projects)",
    )
    dest_group.add_argument(
        "--local",
        action="store_true",
        help="Install into .claude/skills/ (current project only)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report installation state without making changes",
    )
    args = parser.parse_args()

    if args.check:
        _run_check()
        return

    dest = _resolve_destination(args)
    if dest is None:
        sys.exit(1)

    dest.mkdir(parents=True, exist_ok=True)

    print(f"Downloading skills from {GITHUB_REPO} ...")
    installed, updated, skipped = _fetch_and_install(dest)

    _check_claude_in_path()
    _print_summary(installed, updated, skipped, dest)


def _resolve_destination(args: argparse.Namespace) -> Path | None:
    if args.global_:
        return Path.home() / ".claude" / "skills"
    if args.local:
        return Path.cwd() / ".claude" / "skills"

    print("Install SDD skills for Claude Code")
    print("")
    print("  [1] Global (~/.claude/skills/) — available in all projects")
    print("  [2] Project-local (.claude/skills/) — current project only")
    print("")
    try:
        choice = input("Choice [1/2]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return None

    if choice == "1":
        return Path.home() / ".claude" / "skills"
    if choice == "2":
        return Path.cwd() / ".claude" / "skills"

    print("Invalid choice. Use 1 or 2.")
    return None


def _fetch_and_install(dest: Path) -> tuple[list[str], list[str], list[str]]:
    tmp = tempfile.mkdtemp(prefix="sdd-tui-")
    try:
        _clone_repo(tmp)
        skills_src = Path(tmp) / "skills"
        if not skills_src.exists():
            print(f"Error: skills/ not found in cloned repo at {tmp}", file=sys.stderr)
            sys.exit(1)

        installed: list[str] = []
        updated: list[str] = []
        skipped: list[str] = []

        skill_dirs = sorted(
            d for d in skills_src.iterdir() if d.is_dir() and d.name.startswith(SKILLS_PREFIX)
        )

        for skill_dir in skill_dirs:
            name = skill_dir.name
            target = dest / name

            if target.exists():
                action = _prompt_conflict(name)
                if action == "update":
                    shutil.copytree(skill_dir, target, dirs_exist_ok=True)
                    updated.append(name)
                else:
                    skipped.append(name)
            else:
                shutil.copytree(skill_dir, target)
                installed.append(name)

        return installed, updated, skipped
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _clone_repo(dest_dir: str) -> None:
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", "--quiet", GITHUB_REPO, dest_dir],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: git clone failed — {e.stderr.decode().strip()}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: git not found in PATH. Install git and try again.", file=sys.stderr)
        sys.exit(1)


def _prompt_conflict(name: str) -> str:
    """Ask user what to do with an existing skill. Returns 'update' or 'skip'."""
    print(f"\n  {name} is already installed.")
    print("    [u] Update (overwrite)  [s] Skip")
    try:
        choice = input("  Choice [u/s]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "skip"
    return "update" if choice == "u" else "skip"


def _check_claude_in_path() -> None:
    try:
        subprocess.run(["claude", "--version"], capture_output=True, check=False)
    except FileNotFoundError:
        print("")
        print("Note: Claude Code not found in PATH.")
        print("      Install it at https://claude.ai/code")


def _print_summary(
    installed: list[str], updated: list[str], skipped: list[str], dest: Path
) -> None:
    total = len(installed) + len(updated) + len(skipped)
    print("")
    print(f"Done — {total} skill(s) processed")
    print(f"  installed: {len(installed)}  updated: {len(updated)}  skipped: {len(skipped)}")
    print(f"  destination: {dest}")
    print("")
    print("Next steps:")
    print("  1. Restart Claude Code")
    print("  2. Open your project and run /sdd-init")


def _run_check() -> None:
    try:
        version = importlib.metadata.version("sdd-tui")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"

    print(f"sdd-tui version:  {version}")
    print(f"skills source:    {GITHUB_REPO} (main)")
    print("")

    for label, path in [
        ("global", Path.home() / ".claude" / "skills"),
        ("local", Path.cwd() / ".claude" / "skills"),
    ]:
        skills = (
            sorted(
                d.name for d in path.iterdir() if d.is_dir() and d.name.startswith(SKILLS_PREFIX)
            )
            if path.exists()
            else []
        )

        if skills:
            print(f"installed skills ({label} → {path}):")
            for s in skills:
                print(f"  ✓  {s}")
            print("")

    if not any(
        [
            (Path.home() / ".claude" / "skills").exists(),
            (Path.cwd() / ".claude" / "skills").exists(),
        ]
    ):
        print("No skills installed yet. Run `sdd-setup` to install.")
