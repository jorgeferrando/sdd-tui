from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

_SECTION_PATTERN = re.compile(r"^##\s+(added|modified|removed)\b", re.IGNORECASE)
_DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")
_TABLE_ROW = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$")
_SEPARATOR_ROW = re.compile(r"^\|[-| :]+\|$")


@dataclass
class DeltaSpec:
    added: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    fallback: bool = False


@dataclass
class Decision:
    decision: str
    alternative: str
    reason: str


@dataclass
class ChangeDecisions:
    change_name: str
    archive_date: date
    decisions: list[Decision] = field(default_factory=list)


def parse_delta(spec_path: Path) -> DeltaSpec:
    """Parse a delta spec file, extracting ADDED/MODIFIED/REMOVED sections."""
    text = spec_path.read_text(errors="replace")
    lines = text.splitlines()

    buckets: dict[str, list[str]] = {"added": [], "modified": [], "removed": []}
    current: str | None = None

    for line in lines:
        m = _SECTION_PATTERN.match(line)
        if m:
            current = m.group(1).lower()
        elif current is not None:
            buckets[current].append(line)

    if not any(buckets.values()):
        return DeltaSpec(fallback=True)

    return DeltaSpec(
        added=buckets["added"],
        modified=buckets["modified"],
        removed=buckets["removed"],
        fallback=False,
    )


def extract_decisions(design_path: Path, change_name: str) -> ChangeDecisions:
    """Extract the decisions table from a design.md file."""
    # archive_date will be filled by collect_archived_decisions
    result = ChangeDecisions(change_name=change_name, archive_date=date.min)

    if not design_path.exists():
        return result

    text = design_path.read_text(errors="replace")
    lines = text.splitlines()

    in_decisions = False
    header_seen = False

    for line in lines:
        if re.match(r"^##\s+Decisiones Tomadas", line):
            in_decisions = True
            continue

        if in_decisions:
            if line.startswith("## "):
                break
            if _SEPARATOR_ROW.match(line):
                header_seen = True
                continue
            if header_seen:
                m = _TABLE_ROW.match(line)
                if m:
                    result.decisions.append(
                        Decision(
                            decision=m.group(1).strip(),
                            alternative=m.group(2).strip(),
                            reason=m.group(3).strip(),
                        )
                    )

    return result


def collect_archived_decisions(archive_dir: Path) -> list[ChangeDecisions]:
    """Collect decisions from all archived changes, ordered by archive date."""
    results: list[ChangeDecisions] = []

    if not archive_dir.exists():
        return results

    for entry in sorted(archive_dir.iterdir()):
        if not entry.is_dir():
            continue
        m = _DATE_PREFIX.match(entry.name)
        if not m:
            continue

        try:
            archive_date = date.fromisoformat(m.group(1))
        except ValueError:
            continue

        change_name = m.group(2)
        design_path = entry / "design.md"
        cd = extract_decisions(design_path, change_name)
        cd.archive_date = archive_date
        results.append(cd)

    return results
