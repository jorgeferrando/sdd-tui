"""sdd-docs — generate a MkDocs documentation site from openspec/."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Requirement:
    id: str
    type: str
    description: str


@dataclass
class Decision:
    decision: str
    discarded: str
    reason: str


@dataclass
class ChangeEntry:
    name: str
    date: date
    description: str


# ---------------------------------------------------------------------------
# openspec discovery
# ---------------------------------------------------------------------------


def find_git_root(start: Path) -> Path | None:
    """Return the git repository root, or None if not inside a git repo."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        cwd=start,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return None


def find_openspec(start: Path) -> Path | None:
    """Search for openspec/ from `start` up to the git root (or filesystem root)."""
    git_root = find_git_root(start)
    stop = git_root.parent if git_root else Path("/")

    current = start.resolve()
    while current != stop:
        candidate = current / "openspec"
        if candidate.is_dir():
            return candidate
        if current == current.parent:
            break
        current = current.parent
    return None


# ---------------------------------------------------------------------------
# openspec readers
# ---------------------------------------------------------------------------


def load_site_name(openspec: Path) -> str:
    """Derive site name from product.md H1, then config.yaml, then directory name."""
    product = openspec / "steering" / "product.md"
    if product.exists():
        for line in product.read_text(errors="replace").splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()

    config = openspec / "config.yaml"
    if config.exists():
        for line in config.read_text(errors="replace").splitlines():
            m = re.match(r"project_name:\s*(.+)", line)
            if m:
                return m.group(1).strip()

    return openspec.parent.name


def load_site_description(openspec: Path) -> str:
    """Extract the first paragraph from product.md, or return a placeholder."""
    product = openspec / "steering" / "product.md"
    if product.exists():
        text = product.read_text(errors="replace")
        paragraphs = re.split(r"\n{2,}", text.strip())
        for para in paragraphs:
            stripped = para.strip()
            if stripped and not stripped.startswith("#"):
                return stripped.replace("\n", " ")

    return make_placeholder("description", "2-3 sentence overview of the project for end users")


def list_spec_domains(openspec: Path) -> list[str]:
    """Return sorted list of domain names from openspec/specs/."""
    specs_dir = openspec / "specs"
    if not specs_dir.exists():
        return []
    return sorted(d.name for d in specs_dir.iterdir() if d.is_dir())


def parse_spec_requirements(text: str) -> list[Requirement]:
    """Extract EARS requirements from spec markdown text."""
    requirements: list[Requirement] = []
    pattern = re.compile(
        r"\*\*(REQ-[\w-]+)\*\*\s+`\[(\w+)\]`\s+(.+?)(?=\n\s*-\s*\*\*REQ-|\Z)",
        re.DOTALL,
    )
    for m in pattern.finditer(text):
        req_id = m.group(1)
        req_type = m.group(2)
        desc = re.sub(r"\s+", " ", m.group(3)).strip()
        # Trim continuation lines that belong to the next bullet
        desc = desc.split("\n-")[0].strip()
        requirements.append(Requirement(id=req_id, type=req_type, description=desc))
    return requirements


def parse_spec_decisions(text: str) -> list[Decision]:
    """Extract decisions from the markdown table in the spec."""
    decisions: list[Decision] = []
    in_table = False
    header_seen = False

    for line in text.splitlines():
        stripped = line.strip()
        if not in_table:
            if re.match(r"\|\s*Decisi[oó]n\b", stripped, re.IGNORECASE):
                in_table = True
                header_seen = False
                continue
        else:
            if stripped.startswith("|---") or stripped.startswith("| ---"):
                header_seen = True
                continue
            if not stripped.startswith("|"):
                in_table = False
                continue
            if not header_seen:
                continue
            cols = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cols) >= 3:
                decisions.append(Decision(decision=cols[0], discarded=cols[1], reason=cols[2]))

    return decisions


def collect_archived_changes(archive: Path) -> list[ChangeEntry]:
    """Read openspec/changes/archive/ and return entries sorted newest-first."""
    if not archive.exists():
        return []

    entries: list[ChangeEntry] = []
    date_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")

    for change_dir in archive.iterdir():
        if not change_dir.is_dir():
            continue
        m = date_pattern.match(change_dir.name)
        if not m:
            continue
        change_date = date.fromisoformat(m.group(1))
        change_name = m.group(2)

        # proposal.md may be at the top level or nested
        proposal = change_dir / "proposal.md"
        if not proposal.exists():
            nested = change_dir / change_name / "proposal.md"
            if nested.exists():
                proposal = nested

        description = (
            _extract_proposal_description(proposal.read_text(errors="replace"))
            if proposal.exists()
            else change_name
        )

        entries.append(ChangeEntry(name=change_name, date=change_date, description=description))

    entries.sort(key=lambda e: e.date, reverse=True)
    return entries


def _extract_proposal_description(text: str) -> str:
    """Extract the first paragraph under ## Descripción, or first non-empty line."""
    lines = text.splitlines()
    in_section = False
    buffer: list[str] = []

    for line in lines:
        stripped = line.strip()
        if re.match(r"^##\s+Descripci[oó]n", stripped, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("##"):
                break
            if stripped:
                buffer.append(stripped)
            elif buffer:
                break

    if buffer:
        return " ".join(buffer)

    # Fallback: first non-empty, non-heading line
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped

    return ""


# ---------------------------------------------------------------------------
# Content generators (return str)
# ---------------------------------------------------------------------------


def make_placeholder(type_: str, description: str) -> str:
    return f'<!-- sdd-docs:placeholder type="{type_}" description="{description}" -->'


def render_mkdocs_yml(
    site_name: str,
    description: str,
    domains: list[str],
    has_changelog: bool,
) -> str:
    nav_lines = ["nav:"]
    nav_lines.append("  - Home: index.md")

    if domains:
        nav_lines.append("  - Reference:")
        for domain in domains:
            nav_lines.append(f"    - {domain.replace('-', ' ').title()}: reference/{domain}.md")

    if has_changelog:
        nav_lines.append("  - Changelog: changelog.md")

    nav = "\n".join(nav_lines)

    return f"""\
site_name: {site_name}
site_description: {description}

theme:
  name: material
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.top
    - content.code.copy
    - search.highlight
    - search.suggest

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - tables
  - toc:
      permalink: true

{nav}
"""


def render_index_md(site_name: str, description: str) -> str:
    is_placeholder = description.startswith("<!-- sdd-docs:placeholder")
    if is_placeholder:
        description_block = description
    else:
        description_block = description

    quickstart = make_placeholder("quickstart", "Installation and first steps for new users")

    return f"""\
# {site_name}

{description_block}

---

## Quick Start

{quickstart}
"""


def render_reference_page(domain: str, spec_path: Path) -> str:
    text = spec_path.read_text(errors="replace")
    title = domain.replace("-", " ").title()

    requirements = parse_spec_requirements(text)
    decisions = parse_spec_decisions(text)

    lines = [f"# {title} Reference", ""]

    # Summary placeholder
    lines.append(make_placeholder("prose", f"One paragraph overview of the {domain} domain"))
    lines.append("")

    # Requirements table
    if requirements:
        lines += ["## Requirements", ""]
        lines += ["| ID | Type | Description |", "|----|------|-------------|"]
        for req in requirements:
            desc = req.description.replace("|", "\\|")
            lines.append(f"| `{req.id}` | {req.type} | {desc} |")
        lines.append("")

    # Decisions table
    if decisions:
        lines += ["## Decisions", ""]
        lines += [
            "| Decision | Discarded Alternative | Reason |",
            "|----------|----------------------|--------|",
        ]
        for dec in decisions:
            d = dec.decision.replace("|", "\\|")
            a = dec.discarded.replace("|", "\\|")
            r = dec.reason.replace("|", "\\|")
            lines.append(f"| {d} | {a} | {r} |")
        lines.append("")

    return "\n".join(lines)


def render_changelog_md(archive: Path) -> str:
    changes = collect_archived_changes(archive)

    lines = ["# Changelog", ""]

    for entry in changes:
        date_str = entry.date.strftime("%Y-%m-%d")
        desc = entry.description or entry.name
        lines.append(f"- **{date_str}** `{entry.name}` — {desc}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# File writer
# ---------------------------------------------------------------------------


def _write_file(
    path: Path,
    content: str,
    force: bool,
    dry_run: bool,
) -> str:
    """Write file if allowed. Returns 'created', 'skipped', or 'would-create'."""
    if dry_run:
        return "would-create" if not path.exists() else "would-skip"

    if path.exists() and not force:
        return "skipped"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return "created"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sdd-docs",
        description="Generate a MkDocs documentation site from openspec/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be generated without writing anything",
    )
    parser.add_argument(
        "--output",
        metavar="DIR",
        help="Output directory (default: git root)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    args = parser.parse_args()

    # Locate openspec/
    openspec = find_openspec(Path.cwd())
    if openspec is None:
        print(
            "openspec/ not found. Run /sdd-init in Claude Code first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Determine output root
    if args.output:
        out_root = Path(args.output).resolve()
    else:
        git_root = find_git_root(Path.cwd())
        out_root = git_root if git_root else Path.cwd()

    docs_dir = out_root / "docs"
    force = args.force
    dry_run = args.dry_run

    # Gather data
    site_name = load_site_name(openspec)
    description = load_site_description(openspec)
    domains = list_spec_domains(openspec)
    archive = openspec / "changes" / "archive"
    has_changelog = archive.exists() and any(archive.iterdir())

    results: list[tuple[str, str]] = []  # (path_str, status)

    # mkdocs.yml
    mkdocs_content = render_mkdocs_yml(site_name, description, domains, has_changelog)
    status = _write_file(out_root / "mkdocs.yml", mkdocs_content, force, dry_run)
    results.append(("mkdocs.yml", status))

    # docs/index.md
    index_content = render_index_md(site_name, description)
    status = _write_file(docs_dir / "index.md", index_content, force, dry_run)
    results.append(("docs/index.md", status))

    # docs/reference/{domain}.md
    for domain in domains:
        spec_path = openspec / "specs" / domain / "spec.md"
        if not spec_path.exists():
            continue
        page_content = render_reference_page(domain, spec_path)
        rel = f"docs/reference/{domain}.md"
        status = _write_file(out_root / rel, page_content, force, dry_run)
        results.append((rel, status))

    # docs/changelog.md
    if has_changelog:
        changelog_content = render_changelog_md(archive)
        status = _write_file(docs_dir / "changelog.md", changelog_content, force, dry_run)
        results.append(("docs/changelog.md", status))

    # Print summary
    created = [p for p, s in results if s in ("created", "would-create")]
    skipped = [p for p, s in results if s in ("skipped", "would-skip")]

    if dry_run:
        print("DRY RUN — no files written")
        print("")
        for path, status in results:
            marker = "+" if "would-create" in status else "~"
            print(f"  {marker}  {path}")
        print("")
        print(f"Would create: {len(created)}  Would skip: {len(skipped)}")
    else:
        verb = "Overwritten" if force else "Created"
        print(f"sdd-docs: {verb} {len(created)} file(s), skipped {len(skipped)}")
        for path in created:
            print(f"  +  {path}")
        for path in skipped:
            print(f"  ~  {path} (use --force to overwrite)")
        if created:
            print("")
            print("Next: run 'mkdocs serve' to preview, or use /sdd-docs in Claude Code")
            print("      to fill in the placeholder sections.")
