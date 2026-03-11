#!/usr/bin/env python3
"""Generate CHANGELOG.md from openspec/changes/archive/.

Version boundaries are resolved in this order:
  1. git tags (when release_workflow.enabled = true and tags exist)
  2. openspec/versions/*.yaml markers
  3. No boundaries → all changes listed under [Unreleased]

Usage:
  python scripts/changelog.py                  # write CHANGELOG.md
  python scripts/changelog.py --version X.Y.Z  # print section for that version to stdout
  python scripts/changelog.py --mark-version X.Y.Z  # create openspec/versions/X.Y.Z.yaml
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class ChangeEntry:
    name: str
    date: date
    description: str


@dataclass
class VersionBoundary:
    version: str
    date: date
    source: str  # "git-tag" | "marker"


# ---------------------------------------------------------------------------
# Repo / openspec discovery
# ---------------------------------------------------------------------------


def find_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Not inside a git repository")
    return Path(result.stdout.strip())


def _read_release_enabled(root: Path) -> bool:
    config = root / "openspec" / "config.yaml"
    if not config.exists():
        return False
    text = config.read_text(errors="replace")
    in_section = False
    for line in text.splitlines():
        if line.strip() == "release_workflow:":
            in_section = True
            continue
        if in_section:
            if line and not line[0].isspace():
                break
            m = re.match(r"\s+enabled:\s*(\S+)", line)
            if m:
                return m.group(1).lower() == "true"
    return False


def _read_repo_url(root: Path) -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        cwd=root,
    )
    if result.returncode != 0:
        return ""
    url = result.stdout.strip()
    # Normalise SSH → HTTPS
    url = re.sub(r"^git@github\.com:", "https://github.com/", url)
    return url.rstrip("/").removesuffix(".git")


# ---------------------------------------------------------------------------
# Collect archived changes
# ---------------------------------------------------------------------------


def collect_archived_changes(archive_dir: Path) -> list[ChangeEntry]:
    entries: list[ChangeEntry] = []
    if not archive_dir.exists():
        return entries

    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")
    for item in sorted(archive_dir.iterdir()):
        if not item.is_dir():
            continue
        m = pattern.match(item.name)
        if not m:
            continue
        date_str, change_name = m.group(1), m.group(2)
        try:
            entry_date = date.fromisoformat(date_str)
        except ValueError:
            continue

        description = _extract_description(item, change_name)
        entries.append(ChangeEntry(name=change_name, date=entry_date, description=description))

    return entries


def _extract_description(change_dir: Path, change_name: str) -> str:
    # Proposal may be at change_dir/proposal.md or change_dir/{change_name}/proposal.md
    candidates = [
        change_dir / "proposal.md",
        change_dir / change_name / "proposal.md",
    ]
    for proposal in candidates:
        if proposal.exists():
            text = proposal.read_text(errors="replace")
            desc = _parse_description_section(text)
            if desc:
                return desc
    return change_name


def _parse_description_section(text: str) -> str:
    """Return first non-empty, non-heading line after '## Descripción'."""
    in_section = False
    for line in text.splitlines():
        if line.strip() == "## Descripción":
            in_section = True
            continue
        if in_section:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                break
            # Strip markdown list markers and backticks
            stripped = re.sub(r"^[-*]\s+", "", stripped)
            stripped = stripped.rstrip(".")
            return stripped
    # Fallback: first non-empty non-heading line in the file
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("-"):
            return stripped
    return ""


# ---------------------------------------------------------------------------
# Collect version boundaries
# ---------------------------------------------------------------------------


def collect_version_boundaries(root: Path, release_enabled: bool) -> list[VersionBoundary]:
    boundaries: list[VersionBoundary] = []

    if release_enabled:
        boundaries.extend(_boundaries_from_git_tags(root))

    # Always also read markers; deduplicate by version (git tag takes precedence)
    marker_boundaries = _boundaries_from_markers(root)
    existing_versions = {b.version for b in boundaries}
    for mb in marker_boundaries:
        if mb.version not in existing_versions:
            boundaries.append(mb)

    return sorted(boundaries, key=lambda b: b.date, reverse=True)


def _boundaries_from_git_tags(root: Path) -> list[VersionBoundary]:
    result = subprocess.run(
        ["git", "tag", "--sort=-version:refname", "--format=%(refname:short) %(creatordate:short)"],
        capture_output=True,
        text=True,
        cwd=root,
    )
    if result.returncode != 0:
        return []
    boundaries = []
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        tag, date_str = parts[0], parts[1]
        version = tag.lstrip("v")
        if not re.match(r"^\d+\.\d+", version):
            continue
        try:
            boundaries.append(VersionBoundary(version=version, date=date.fromisoformat(date_str), source="git-tag"))
        except ValueError:
            continue
    return boundaries


def _boundaries_from_markers(root: Path) -> list[VersionBoundary]:
    versions_dir = root / "openspec" / "versions"
    if not versions_dir.exists():
        return []
    boundaries = []
    for f in versions_dir.iterdir():
        if not f.is_file() or f.suffix != ".yaml":
            continue
        version = f.stem
        if not re.match(r"^\d+\.\d+", version):
            continue
        marker_date = _read_marker_date(f) or date.today()
        boundaries.append(VersionBoundary(version=version, date=marker_date, source="marker"))
    return boundaries


def _read_marker_date(marker_file: Path) -> date | None:
    for line in marker_file.read_text(errors="replace").splitlines():
        m = re.match(r"date:\s*(\d{4}-\d{2}-\d{2})", line.strip())
        if m:
            try:
                return date.fromisoformat(m.group(1))
            except ValueError:
                pass
    return None


# ---------------------------------------------------------------------------
# Assign changes to versions
# ---------------------------------------------------------------------------


def assign_changes_to_versions(
    changes: list[ChangeEntry],
    boundaries: list[VersionBoundary],
) -> dict[str, list[ChangeEntry]]:
    """Returns OrderedDict-like: version → [changes], newest first.
    Key "[Unreleased]" holds changes not covered by any boundary.
    """
    result: dict[str, list[ChangeEntry]] = {}

    # Sort boundaries newest → oldest
    sorted_boundaries = sorted(boundaries, key=lambda b: b.date, reverse=True)

    for change in sorted(changes, key=lambda c: c.date, reverse=True):
        assigned = False
        for boundary in sorted_boundaries:
            if change.date <= boundary.date:
                result.setdefault(boundary.version, []).append(change)
                assigned = True
                break
        if not assigned:
            result.setdefault("[Unreleased]", []).append(change)

    return result


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


def render_changelog(
    assignments: dict[str, list[ChangeEntry]],
    boundaries: list[VersionBoundary],
    repo_url: str,
) -> str:
    lines = [
        "# Changelog",
        "",
        "Generated from `openspec/changes/archive/`.",
        "",
    ]

    # [Unreleased] first
    if "[Unreleased]" in assignments:
        lines.append("## [Unreleased]")
        lines.append("")
        for entry in assignments["[Unreleased]"]:
            lines.append(f"- `{entry.name}`: {entry.description}")
        lines.append("")

    # Versioned sections, newest first
    boundary_map = {b.version: b for b in boundaries}
    for version in sorted(assignments.keys(), key=lambda v: _version_sort_key(v, boundary_map), reverse=True):
        if version == "[Unreleased]":
            continue
        boundary = boundary_map.get(version)
        date_str = boundary.date.isoformat() if boundary else "unknown"
        lines.append(f"## [{version}] — {date_str}")
        lines.append("")
        for entry in assignments[version]:
            lines.append(f"- `{entry.name}`: {entry.description}")
        lines.append("")

    # Reference links
    if repo_url:
        sorted_versions = [v for v in assignments if v != "[Unreleased]"]
        sorted_versions.sort(key=lambda v: _version_sort_key(v, boundary_map), reverse=True)

        if "[Unreleased]" in assignments and sorted_versions:
            lines.append(f"[Unreleased]: {repo_url}/compare/v{sorted_versions[0]}...HEAD")
        for i, version in enumerate(sorted_versions):
            prev = sorted_versions[i + 1] if i + 1 < len(sorted_versions) else None
            if prev:
                lines.append(f"[{version}]: {repo_url}/compare/v{prev}...v{version}")
            else:
                lines.append(f"[{version}]: {repo_url}/releases/tag/v{version}")

    return "\n".join(lines) + "\n"


def _version_sort_key(version: str, boundary_map: dict) -> tuple:
    boundary = boundary_map.get(version)
    if boundary:
        return (boundary.date.toordinal(),)
    # Fallback: parse version numbers
    parts = re.findall(r"\d+", version)
    return tuple(int(p) for p in parts)


def extract_section(changelog_text: str, version: str) -> str:
    """Extract the release notes for a specific version from CHANGELOG.md text."""
    lines = changelog_text.splitlines()
    in_section = False
    section_lines: list[str] = []
    header = f"## [{version}]"

    for line in lines:
        if line.startswith(header):
            in_section = True
            continue
        if in_section:
            if line.startswith("## [") or line.startswith("["):
                break
            section_lines.append(line)

    return "\n".join(section_lines).strip()


# ---------------------------------------------------------------------------
# mark-version
# ---------------------------------------------------------------------------


def mark_version(root: Path, version: str) -> Path:
    """Create openspec/versions/X.Y.Z.yaml with today's date."""
    versions_dir = root / "openspec" / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    marker = versions_dir / f"{version}.yaml"
    marker.write_text(f"date: {date.today().isoformat()}\n")
    return marker


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CHANGELOG.md from openspec/")
    parser.add_argument("--version", metavar="X.Y.Z", help="Print release notes for this version to stdout")
    parser.add_argument("--mark-version", metavar="X.Y.Z", help="Create openspec/versions/X.Y.Z.yaml")
    args = parser.parse_args()

    try:
        root = find_repo_root()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.mark_version:
        marker = mark_version(root, args.mark_version)
        print(f"Created: {marker}")
        return

    release_enabled = _read_release_enabled(root)
    archive_dir = root / "openspec" / "changes" / "archive"
    changes = collect_archived_changes(archive_dir)
    boundaries = collect_version_boundaries(root, release_enabled)
    assignments = assign_changes_to_versions(changes, boundaries)
    repo_url = _read_repo_url(root)
    changelog = render_changelog(assignments, boundaries, repo_url)

    if args.version:
        section = extract_section(changelog, args.version)
        print(section)
        return

    output = root / "CHANGELOG.md"
    output.write_text(changelog)
    print(f"Written: {output}")


if __name__ == "__main__":
    main()
