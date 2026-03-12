"""AI-powered documentation generation for sdd-docs.

Architecture
------------
LLMProvider is a Protocol — any object with a ``generate(system, prompt)`` method
qualifies. ``make_provider()`` returns the first available implementation based on
environment variables. Adding a new LLM is:
  1. Implement a class with ``generate()``.
  2. Add an ``if os.environ.get("NEW_LLM_API_KEY")`` block in ``make_provider()``.

Current providers
-----------------
- AnthropicProvider — requires ``anthropic`` package + ``ANTHROPIC_API_KEY``

Future providers (not yet implemented)
---------------------------------------
- OpenAIProvider  — OPENAI_API_KEY  (Codex / GPT)
- GeminiProvider  — GEMINI_API_KEY
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Provider protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class LLMProvider(Protocol):
    """Minimal contract for a text-generation LLM."""

    def generate(self, system: str, prompt: str, max_tokens: int = 2048) -> str:
        """Return the model's text response."""
        ...


# ---------------------------------------------------------------------------
# Anthropic implementation
# ---------------------------------------------------------------------------

class AnthropicProvider:
    """Claude via the Anthropic SDK. Reads ANTHROPIC_API_KEY from the environment."""

    MODEL = "claude-haiku-4-5-20251001"

    def generate(self, system: str, prompt: str, max_tokens: int = 2048) -> str:
        import anthropic  # lazy — optional dep

        client = anthropic.Anthropic()
        message = client.messages.create(
            model=self.MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def make_provider() -> LLMProvider | None:
    """Return the first available LLM provider, or None.

    Priority order (first env var set wins):
      1. ANTHROPIC_API_KEY  → AnthropicProvider
      # 2. OPENAI_API_KEY   → OpenAIProvider   (future)
      # 3. GEMINI_API_KEY   → GeminiProvider   (future)
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic  # noqa: F401 — verify package is installed
            return AnthropicProvider()
        except ImportError:
            pass  # anthropic package not installed
    return None


def is_available() -> bool:
    """Return True if at least one LLM provider is available."""
    return make_provider() is not None


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def build_context(openspec: Path, site_name: str) -> str:
    """Collect project context from openspec/ into a plain-text summary."""
    lines: list[str] = [f"Project: {site_name}", ""]

    # Spec domains
    specs_dir = openspec / "specs"
    if specs_dir.exists():
        domains = sorted(d.name for d in specs_dir.iterdir() if d.is_dir())
        lines.append(f"Spec domains ({len(domains)}): {', '.join(domains)}")
        lines.append("")

        for domain in domains:
            spec_file = specs_dir / domain / "spec.md"
            if spec_file.exists():
                text = spec_file.read_text(errors="replace")
                req_count = text.count("**REQ-")
                lines.append(f"  {domain}: {req_count} requirements")
        lines.append("")

    # Archive summary
    archive = openspec / "changes" / "archive"
    if archive.exists():
        change_dirs = [d for d in archive.iterdir() if d.is_dir()]
        lines.append(f"Archived changes: {len(change_dirs)}")
        lines.append("")

    # Steering files
    steering_dir = openspec / "steering"
    for fname in ("product.md", "tech.md", "structure.md"):
        fpath = steering_dir / fname
        if fpath.exists():
            content = fpath.read_text(errors="replace").strip()
            lines.append(f"--- {fname} ---")
            lines.append(content[:1500])  # cap to avoid huge prompts
            lines.append("")

    # README
    for readme_name in ("README.md", "readme.md"):
        readme = openspec.parent / readme_name
        if readme.exists():
            content = readme.read_text(errors="replace").strip()
            lines.append("--- README.md ---")
            lines.append(content[:2000])
            lines.append("")
            break

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Generation functions (each receives an injected provider — easier to test)
# ---------------------------------------------------------------------------

_SYSTEM = (
    "You are a technical documentation writer. "
    "Generate clean, concise Markdown documentation. "
    "No preamble, no explanation — output only the requested content."
)


def fill_index(provider: LLMProvider, context: str, site_name: str) -> str:
    """Generate a complete docs/index.md for the project."""
    prompt = f"""\
Generate a complete docs/index.md for a project called "{site_name}".

Project context:
{context}

The page must include:
- H1 title: {site_name}
- A "The problem" section (2-3 paragraphs) — why this project exists
- A "Two tools" or similar section explaining the main components
- A brief ASCII/text demo or code block showing the tool in action
- A "Quick start" section with install and first-run commands
- A "Core idea" section with a mermaid flowchart if the workflow is sequential

Use GitHub-flavored Markdown. Output only the Markdown, starting with the H1.
"""
    return provider.generate(_SYSTEM, prompt, max_tokens=2048)


def fill_mkdocs(
    provider: LLMProvider,
    context: str,
    site_name: str,
    nav_block: str,
) -> str:
    """Generate a complete mkdocs.yml. nav_block is already computed mechanically."""
    prompt = f"""\
Generate a complete mkdocs.yml for a MkDocs Material site called "{site_name}".

Project context:
{context}

Requirements:
- site_name: {site_name}
- site_description: one sentence about the project (derive from context)
- Material theme with light/dark palette toggle (primary: indigo)
- features: navigation.tabs, navigation.sections, navigation.top, navigation.footer,
  content.code.copy, search.highlight, search.suggest
- markdown_extensions: admonition, pymdownx.details,
  pymdownx.superfences with mermaid custom fence (class mermaid),
  pymdownx.tabbed (alternate_style: true),
  pymdownx.highlight (anchor_linenums: true),
  pymdownx.inlinehilite, tables, attr_list, md_in_html,
  toc (permalink: true)
- Use this nav block verbatim:
{nav_block}

Output only valid YAML. No backticks, no explanation.
"""
    return provider.generate(_SYSTEM, prompt, max_tokens=1024)


def fill_reference_prose(provider: LLMProvider, domain: str, context: str) -> str:
    """Generate a prose paragraph for a reference page."""
    prompt = f"""\
Write a single paragraph (3-5 sentences) describing the "{domain}" domain
for the project. It will appear at the top of the reference documentation page,
before the requirements table.

Project context:
{context}

Be concise and technical. Address what the domain covers and why it matters.
Output only the paragraph — no heading, no Markdown formatting.
"""
    return provider.generate(_SYSTEM, prompt, max_tokens=300)
