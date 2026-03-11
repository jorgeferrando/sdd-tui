from __future__ import annotations

import json
import re
from pathlib import Path

from sdd_tui.core.config import AppConfig
from sdd_tui.core.models import Change, OpenspecNotFoundError
from sdd_tui.core.providers.protocol import GitWorkflowConfig, ReleaseWorkflowConfig


def load_git_workflow_config(openspec_path: Path) -> GitWorkflowConfig:
    """Read the git_workflow: section from openspec/config.yaml, returning defaults on any error."""
    config_file = openspec_path / "config.yaml"
    if not config_file.exists():
        return GitWorkflowConfig()
    try:
        return _parse_git_workflow(config_file.read_text(errors="replace"))
    except Exception:
        return GitWorkflowConfig()


def _parse_git_workflow(text: str) -> GitWorkflowConfig:
    defaults = GitWorkflowConfig()
    kwargs: dict[str, str] = {}
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "git_workflow:":
            in_section = True
            continue
        if in_section:
            if not stripped or stripped.startswith("#"):
                continue
            # End of section when a new top-level key appears (no leading whitespace)
            if line and not line[0].isspace():
                break
            m = re.match(r"\s+(\w+):\s*(.+)", line)
            if m:
                kwargs[m.group(1)] = m.group(2).strip()
    # Only set fields that exist on GitWorkflowConfig
    valid = {f for f in defaults.__dataclass_fields__}
    filtered = {k: v for k, v in kwargs.items() if k in valid}
    return GitWorkflowConfig(**filtered)


def _write_git_workflow_config(openspec_path: Path, cfg: GitWorkflowConfig) -> None:
    """Write or replace the git_workflow: section in openspec/config.yaml."""
    config_file = openspec_path / "config.yaml"

    block_lines = [
        "git_workflow:",
        f"  issue_tracker: {cfg.issue_tracker}",
        f"  git_host: {cfg.git_host}",
        f"  branching_model: {cfg.branching_model}",
        f"  change_prefix: {cfg.change_prefix}",
        f"  changelog_format: {cfg.changelog_format}",
    ]
    block = "\n".join(block_lines) + "\n"

    if not config_file.exists():
        openspec_path.mkdir(parents=True, exist_ok=True)
        config_file.write_text("# Añadir jira_prefix: si usas SDD\n" + block)
        return

    existing = config_file.read_text(errors="replace")
    lines = existing.splitlines(keepends=True)

    # Find start and end of existing git_workflow: section
    start = None
    end = len(lines)
    for i, line in enumerate(lines):
        if line.strip() == "git_workflow:":
            start = i
            continue
        if start is not None and i > start:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if line and not line[0].isspace():
                end = i
                break

    if start is not None:
        new_lines = lines[:start] + [block] + lines[end:]
        config_file.write_text("".join(new_lines))
    else:
        # Append at the end, ensuring a newline separator
        if existing and not existing.endswith("\n"):
            existing += "\n"
        config_file.write_text(existing + block)


def load_release_config(openspec_path: Path) -> tuple[ReleaseWorkflowConfig, bool]:
    """Read the release_workflow: section from openspec/config.yaml.

    Returns (config, is_configured).
    is_configured=False when the section is absent (user has not set it up yet).
    is_configured=True even when enabled=False (user explicitly opted out).
    """
    config_file = openspec_path / "config.yaml"
    if not config_file.exists():
        return ReleaseWorkflowConfig(), False
    try:
        text = config_file.read_text(errors="replace")
        if "release_workflow:" not in text:
            return ReleaseWorkflowConfig(), False
        return _parse_release_workflow(text), True
    except Exception:
        return ReleaseWorkflowConfig(), False


def _parse_release_workflow(text: str) -> ReleaseWorkflowConfig:
    raw: dict[str, str] = {}
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "release_workflow:":
            in_section = True
            continue
        if in_section:
            if not stripped or stripped.startswith("#"):
                continue
            if line and not line[0].isspace():
                break
            m = re.match(r"\s+(\w+):\s*(.+)", line)
            if m:
                raw[m.group(1)] = m.group(2).strip()

    kwargs: dict = {}
    if "enabled" in raw:
        kwargs["enabled"] = raw["enabled"].lower() == "true"
    if "versioning" in raw:
        kwargs["versioning"] = raw["versioning"]
    if "changelog_source" in raw:
        kwargs["changelog_source"] = raw["changelog_source"]
    if "homebrew_formula" in raw:
        val = raw["homebrew_formula"]
        kwargs["homebrew_formula"] = None if val in ("null", "none", "~") else val
    return ReleaseWorkflowConfig(**kwargs)


def _write_release_config(openspec_path: Path, cfg: ReleaseWorkflowConfig) -> None:
    """Write or replace the release_workflow: section in openspec/config.yaml."""
    config_file = openspec_path / "config.yaml"

    formula_val = cfg.homebrew_formula if cfg.homebrew_formula else "null"
    block_lines = [
        "release_workflow:",
        f"  enabled: {str(cfg.enabled).lower()}",
        f"  versioning: {cfg.versioning}",
        f"  changelog_source: {cfg.changelog_source}",
        f"  homebrew_formula: {formula_val}",
    ]
    block = "\n".join(block_lines) + "\n"

    if not config_file.exists():
        openspec_path.mkdir(parents=True, exist_ok=True)
        config_file.write_text(block)
        return

    existing = config_file.read_text(errors="replace")
    lines = existing.splitlines(keepends=True)

    start = None
    end = len(lines)
    for i, line in enumerate(lines):
        if line.strip() == "release_workflow:":
            start = i
            continue
        if start is not None and i > start:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if line and not line[0].isspace():
                end = i
                break

    if start is not None:
        new_lines = lines[:start] + [block] + lines[end:]
        config_file.write_text("".join(new_lines))
    else:
        if existing and not existing.endswith("\n"):
            existing += "\n"
        config_file.write_text(existing + block)


def load_steering(openspec_path: Path) -> str | None:
    """Return content of openspec/steering.md, or None if not present."""
    path = openspec_path / "steering.md"
    if not path.exists():
        return None
    return path.read_text(errors="replace")


def load_spec_json(change_path: Path) -> dict | None:
    """Return parsed spec.json for a change, or None if missing or malformed."""
    path = change_path / "spec.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(errors="replace"))
    except (json.JSONDecodeError, OSError):
        return None


class OpenspecReader:
    def load(
        self,
        openspec_path: Path,
        include_archived: bool = False,
        project_path: Path | None = None,
    ) -> list[Change]:
        changes_path = openspec_path / "changes"
        if not openspec_path.exists() or not changes_path.exists():
            raise OpenspecNotFoundError(f"openspec/ not found at {openspec_path}")

        proj = project_path or openspec_path.parent

        entries = sorted(
            entry for entry in changes_path.iterdir() if entry.is_dir() and entry.name != "archive"
        )
        changes = [
            Change(name=entry.name, path=entry, project=proj.name, project_path=proj)
            for entry in entries
        ]

        if include_archived:
            archive_path = changes_path / "archive"
            if archive_path.exists():
                archived_entries = sorted(
                    entry for entry in archive_path.iterdir() if entry.is_dir()
                )
                changes += [
                    Change(
                        name=entry.name,
                        path=entry,
                        archived=True,
                        project=proj.name,
                        project_path=proj,
                    )
                    for entry in archived_entries
                ]

        return changes


def load_all_changes(config: AppConfig, cwd: Path, include_archived: bool = False) -> list[Change]:
    """Return flat list of Changes from all configured projects.

    If config.projects is empty, falls back to single-project mode using cwd.
    Projects whose openspec/ is missing are skipped silently.
    """
    reader = OpenspecReader()
    if not config.projects:
        return reader.load(cwd / "openspec", include_archived, project_path=cwd)

    all_changes: list[Change] = []
    for pc in config.projects:
        try:
            all_changes.extend(
                reader.load(pc.path / "openspec", include_archived, project_path=pc.path)
            )
        except OpenspecNotFoundError:
            pass
    return all_changes
