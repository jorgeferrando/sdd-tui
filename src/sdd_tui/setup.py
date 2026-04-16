"""sdd-setup — installs SDD skills from GitHub for any AI coding tool."""

from __future__ import annotations

import argparse
import importlib.metadata
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GITHUB_REPO = "https://github.com/jorgeferrando/sdd-skills"
SKILLS_PREFIX = "sdd-"

TOOL_CONFIG = {
    "claude": {
        "label": "Claude Code",
        "skill_filename": "SKILL.md",
        "local_dest": lambda: Path.cwd() / ".claude" / "skills",
        "global_dest": lambda: Path.home() / ".claude" / "skills",
        "has_global": True,
    },
    "cursor": {
        "label": "Cursor",
        "skill_filename": "instructions.md",
        "local_dest": lambda: Path.cwd() / ".cursor" / "rules" / "sdd",
        "global_dest": None,
        "has_global": False,
    },
    "codex": {
        "label": "Codex (OpenAI)",
        "skill_filename": "instructions.md",
        "local_dest": lambda: Path.cwd() / ".sdd" / "skills",
        "global_dest": None,
        "has_global": False,
    },
    "copilot": {
        "label": "GitHub Copilot",
        "skill_filename": "instructions.md",
        "local_dest": lambda: Path.cwd() / ".github" / "sdd",
        "global_dest": None,
        "has_global": False,
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sdd-setup",
        description="Install SDD skills from GitHub for any AI coding tool.",
    )
    parser.add_argument(
        "--tool",
        choices=list(TOOL_CONFIG.keys()),
        help="AI coding tool (claude, cursor, codex, copilot)",
    )
    dest_group = parser.add_mutually_exclusive_group()
    dest_group.add_argument(
        "--global",
        dest="global_",
        action="store_true",
        help="Install globally (Claude Code only)",
    )
    dest_group.add_argument(
        "--local",
        action="store_true",
        help="Install into current project",
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

    tool = args.tool or _prompt_tool()
    if tool is None:
        sys.exit(1)

    config = TOOL_CONFIG[tool]
    dest = _resolve_destination(args, config)
    if dest is None:
        sys.exit(1)

    dest.mkdir(parents=True, exist_ok=True)

    print(f"Downloading skills from {GITHUB_REPO} ...")
    installed, updated, skipped = _fetch_and_install(dest, config["skill_filename"])

    _print_summary(installed, updated, skipped, dest, config["label"])


def _prompt_tool() -> str | None:
    print("Install SDD skills")
    print("")
    print("  Which AI coding tool do you use?")
    print("    [1] Claude Code")
    print("    [2] Cursor")
    print("    [3] Codex (OpenAI)")
    print("    [4] GitHub Copilot")
    print("")
    try:
        choice = input("Choice [1/2/3/4]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return None

    tools = {"1": "claude", "2": "cursor", "3": "codex", "4": "copilot"}
    if choice not in tools:
        print("Invalid choice.")
        return None
    return tools[choice]


def _resolve_destination(args: argparse.Namespace, config: dict) -> Path | None:
    if args.global_:
        if not config["has_global"]:
            print(f"Error: --global is only supported for Claude Code.")
            return None
        return config["global_dest"]()
    if args.local:
        return config["local_dest"]()

    if not config["has_global"]:
        return config["local_dest"]()

    print("")
    print(f"  [1] Global ({config['global_dest']()}) — available in all projects")
    print(f"  [2] Project-local ({config['local_dest']()}) — current project only")
    print("")
    try:
        choice = input("  Choice [1/2]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return None

    if choice == "1":
        return config["global_dest"]()
    if choice == "2":
        return config["local_dest"]()

    print("Invalid choice. Use 1 or 2.")
    return None


def _fetch_and_install(
    dest: Path, skill_filename: str
) -> tuple[list[str], list[str], list[str]]:
    tmp = tempfile.mkdtemp(prefix="sdd-skills-")
    try:
        _clone_repo(tmp)
        skills_src = Path(tmp) / "skills"
        if not skills_src.exists() or not any(skills_src.iterdir()):
            print(f"Error: skills/ directory not found in cloned repo", file=sys.stderr)
            sys.exit(1)

        installed: list[str] = []
        updated: list[str] = []
        skipped: list[str] = []

        skill_dirs = sorted(
            d
            for d in skills_src.iterdir()
            if d.is_dir() and d.name.startswith(SKILLS_PREFIX)
        )

        for skill_dir in skill_dirs:
            name = skill_dir.name
            target = dest / name

            # Find the source instruction file
            src_file = skill_dir / skill_filename
            if not src_file.exists():
                # Fallback: copy instructions.md as the target filename
                src_file = skill_dir / "instructions.md"
            if not src_file.exists():
                continue

            if target.exists():
                action = _prompt_conflict(name)
                if action == "update":
                    target.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, target / skill_filename)
                    updated.append(name)
                else:
                    skipped.append(name)
            else:
                target.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, target / skill_filename)
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
        print(
            f"Error: git clone failed — {e.stderr.decode().strip()}", file=sys.stderr
        )
        sys.exit(1)
    except FileNotFoundError:
        print(
            "Error: git not found in PATH. Install git and try again.", file=sys.stderr
        )
        sys.exit(1)


def _prompt_conflict(name: str) -> str:
    print(f"\n  {name} is already installed.")
    print("    [u] Update (overwrite)  [s] Skip")
    try:
        choice = input("  Choice [u/s]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "skip"
    return "update" if choice == "u" else "skip"


def _print_summary(
    installed: list[str],
    updated: list[str],
    skipped: list[str],
    dest: Path,
    tool_label: str,
) -> None:
    total = len(installed) + len(updated) + len(skipped)
    print("")
    print(f"Done — {total} skill(s) processed for {tool_label}")
    print(
        f"  installed: {len(installed)}  updated: {len(updated)}  skipped: {len(skipped)}"
    )
    print(f"  destination: {dest}")
    print("")
    print("Next steps:")
    print("  1. Restart your editor")
    print("  2. Open your project and run /sdd-init")


def _run_check() -> None:
    try:
        version = importlib.metadata.version("sdd-tui")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"

    print(f"sdd-tui version:  {version}")
    print(f"skills source:    {GITHUB_REPO} (main)")
    print("")

    for tool_key, config in TOOL_CONFIG.items():
        for label, path_fn in [("local", config["local_dest"])]:
            path = path_fn()
            if path.exists():
                skills = sorted(
                    d.name
                    for d in path.iterdir()
                    if d.is_dir() and d.name.startswith(SKILLS_PREFIX)
                )
                if skills:
                    print(f"installed skills ({config['label']} {label} → {path}):")
                    for s in skills:
                        print(f"  ✓  {s}")
                    print("")

        if config["has_global"] and config["global_dest"]:
            gpath = config["global_dest"]()
            if gpath.exists():
                skills = sorted(
                    d.name
                    for d in gpath.iterdir()
                    if d.is_dir() and d.name.startswith(SKILLS_PREFIX)
                )
                if skills:
                    print(f"installed skills ({config['label']} global → {gpath}):")
                    for s in skills:
                        print(f"  ✓  {s}")
                    print("")

    found_any = any(
        config["local_dest"]().exists()
        or (config["has_global"] and config["global_dest"] and config["global_dest"]().exists())
        for config in TOOL_CONFIG.values()
    )
    if not found_any:
        print("No skills installed yet. Run `sdd-setup` to install.")
