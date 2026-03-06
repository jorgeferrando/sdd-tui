from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Skills with prefix "sdd-" that accept a {change_name} argument.
# Exceptions (no change arg): sdd-new, sdd-explore, sdd-ff, sdd-init, sdd-propose.
_CONTEXT_AWARE: frozenset[str] = frozenset(
    {
        "sdd-apply",
        "sdd-archive",
        "sdd-audit",
        "sdd-continue",
        "sdd-design",
        "sdd-spec",
        "sdd-steer",
        "sdd-tasks",
        "sdd-verify",
    }
)


@dataclass
class SkillInfo:
    name: str
    description: str


def load_skills(skills_dir: Path) -> list[SkillInfo]:
    """Scan skills_dir and return list[SkillInfo] sorted SDD-first, then alphabetical."""
    if not skills_dir.exists():
        return []

    sdd: list[SkillInfo] = []
    rest: list[SkillInfo] = []

    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        try:
            text = skill_md.read_text(errors="replace")
        except OSError:
            continue
        fields = _parse_front_matter(text)
        name = fields.get("name", "").strip()
        description = fields.get("description", "").strip()
        if not name or not description:
            continue
        info = SkillInfo(name=name, description=description)
        if name.startswith("sdd-"):
            sdd.append(info)
        else:
            rest.append(info)

    return sorted(sdd, key=lambda s: s.name) + sorted(rest, key=lambda s: s.name)


def _parse_front_matter(text: str) -> dict[str, str]:
    """Extract key: value pairs from a YAML front matter block (--- ... ---)."""
    if not text.startswith("---"):
        return {}
    result: dict[str, str] = {}
    lines = text.splitlines()
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([\w-]+):\s+(.+)$", line)
        if m:
            result[m.group(1)] = m.group(2).strip()
    return result
