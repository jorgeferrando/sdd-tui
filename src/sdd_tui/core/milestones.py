from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Milestone:
    name: str
    changes: list[str] = field(default_factory=list)


def load_milestones(openspec_path: Path) -> list[Milestone]:
    yaml_path = openspec_path / "milestones.yaml"
    if not yaml_path.exists():
        return []
    try:
        return _parse_milestones(yaml_path.read_text(errors="replace"))
    except Exception:
        return []


def _parse_milestones(text: str) -> list[Milestone]:
    milestones: list[Milestone] = []
    current_name: str | None = None
    current_changes: list[str] = []
    in_milestones = False
    in_changes = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped == "milestones:":
            in_milestones = True
            continue

        if not in_milestones:
            continue

        # New top-level key exits milestones block
        if not line.startswith(" "):
            break

        # New milestone entry: "  - name: ..."
        m = re.match(r"  - name:\s*(.+)", line)
        if m:
            if current_name is not None:
                milestones.append(Milestone(name=current_name, changes=current_changes))
            current_name = m.group(1).strip().strip("\"'")
            current_changes = []
            in_changes = False
            continue

        # Start of changes block: "    changes:"
        if re.match(r"    changes:", line):
            in_changes = True
            continue

        # Change entry: "      - change-name"
        if in_changes:
            m2 = re.match(r"\s{6}-\s+(.+)", line)
            if m2:
                current_changes.append(m2.group(1).strip())

    if current_name is not None:
        milestones.append(Milestone(name=current_name, changes=current_changes))

    return milestones
