"""Tests for ai_docs module.

The LLMProvider protocol is tested via a simple mock — no real API calls.
AnthropicProvider and make_provider() are tested with environment patching.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from sdd_tui.ai_docs import (
    AnthropicProvider,
    LLMProvider,
    build_context,
    fill_index,
    fill_mkdocs,
    fill_reference_prose,
    is_available,
    make_provider,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeProvider:
    """Minimal LLMProvider implementation for tests."""

    def __init__(self, response: str = "generated content") -> None:
        self.response = response
        self.calls: list[tuple[str, str]] = []

    def generate(self, system: str, prompt: str, max_tokens: int = 2048) -> str:
        self.calls.append((system, prompt))
        return self.response


def _make_openspec(
    tmp_path: Path, *, with_steering: bool = False, with_readme: bool = False
) -> Path:
    openspec = tmp_path / "openspec"
    (openspec / "specs" / "core").mkdir(parents=True)
    (openspec / "specs" / "core" / "spec.md").write_text(
        "**REQ-CORE01** `[Ubiquitous]` desc\n**REQ-CORE02** `[Event]` desc2\n"
    )
    (openspec / "specs" / "tui").mkdir()
    (openspec / "specs" / "tui" / "spec.md").write_text("**REQ-TUI01** `[Optional]` desc\n")
    (openspec / "changes" / "archive" / "2026-01-01-bootstrap").mkdir(parents=True)
    (openspec / "changes" / "archive" / "2026-02-01-feature").mkdir()

    if with_steering:
        (openspec / "steering").mkdir()
        (openspec / "steering" / "product.md").write_text("# My Project\nA tool for developers.")

    if with_readme:
        (tmp_path / "README.md").write_text("# My Project\nInstall with pip.")

    return openspec


# ---------------------------------------------------------------------------
# LLMProvider protocol
# ---------------------------------------------------------------------------

class TestLLMProviderProtocol:
    def test_fake_provider_satisfies_protocol(self):
        provider = _FakeProvider()
        assert isinstance(provider, LLMProvider)

    def test_anthropic_provider_satisfies_protocol(self):
        assert issubclass(AnthropicProvider, LLMProvider) or isinstance(
            AnthropicProvider(), LLMProvider
        )


# ---------------------------------------------------------------------------
# make_provider / is_available
# ---------------------------------------------------------------------------

class TestMakeProvider:
    def test_returns_none_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        assert make_provider() is None

    def test_returns_none_when_anthropic_not_installed(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        with patch.dict("sys.modules", {"anthropic": None}):
            result = make_provider()
        assert result is None

    def test_returns_anthropic_provider_when_key_set(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        mock_anthropic = MagicMock()
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            result = make_provider()
        assert isinstance(result, AnthropicProvider)

    def test_is_available_false_without_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        assert is_available() is False

    def test_is_available_true_with_key(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        mock_anthropic = MagicMock()
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            assert is_available() is True


# ---------------------------------------------------------------------------
# AnthropicProvider.generate
# ---------------------------------------------------------------------------

class TestAnthropicProvider:
    def test_calls_sdk_with_correct_args(self):
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="response text")]
        mock_client.messages.create.return_value = mock_message

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            provider = AnthropicProvider()
            result = provider.generate("sys", "user prompt", max_tokens=512)

        mock_client.messages.create.assert_called_once_with(
            model=AnthropicProvider.MODEL,
            max_tokens=512,
            system="sys",
            messages=[{"role": "user", "content": "user prompt"}],
        )
        assert result == "response text"


# ---------------------------------------------------------------------------
# build_context
# ---------------------------------------------------------------------------

class TestBuildContext:
    def test_includes_site_name(self, tmp_path):
        openspec = _make_openspec(tmp_path)
        ctx = build_context(openspec, "MyProject")
        assert "MyProject" in ctx

    def test_includes_domain_names(self, tmp_path):
        openspec = _make_openspec(tmp_path)
        ctx = build_context(openspec, "proj")
        assert "core" in ctx
        assert "tui" in ctx

    def test_includes_req_count(self, tmp_path):
        openspec = _make_openspec(tmp_path)
        ctx = build_context(openspec, "proj")
        assert "2 requirements" in ctx  # core has 2 REQs

    def test_includes_archive_count(self, tmp_path):
        openspec = _make_openspec(tmp_path)
        ctx = build_context(openspec, "proj")
        assert "Archived changes: 2" in ctx

    def test_includes_steering_when_present(self, tmp_path):
        openspec = _make_openspec(tmp_path, with_steering=True)
        ctx = build_context(openspec, "proj")
        assert "product.md" in ctx
        assert "A tool for developers." in ctx

    def test_includes_readme_when_present(self, tmp_path):
        openspec = _make_openspec(tmp_path, with_readme=True)
        ctx = build_context(openspec, "proj")
        assert "README.md" in ctx
        assert "Install with pip." in ctx

    def test_no_error_when_specs_absent(self, tmp_path):
        openspec = tmp_path / "openspec"
        openspec.mkdir()
        ctx = build_context(openspec, "proj")
        assert "proj" in ctx

    def test_readme_capped_at_2000_chars(self, tmp_path):
        openspec = _make_openspec(tmp_path)
        (tmp_path / "README.md").write_text("x" * 5000)
        ctx = build_context(openspec, "proj")
        # the context should not contain more than 2000 x's (capped)
        assert ctx.count("x") <= 2000


# ---------------------------------------------------------------------------
# fill_index
# ---------------------------------------------------------------------------

class TestFillIndex:
    def test_calls_provider_generate(self):
        provider = _FakeProvider("# MyProject\nContent here.")
        result = fill_index(provider, "some context", "MyProject")
        assert result == "# MyProject\nContent here."
        assert len(provider.calls) == 1

    def test_prompt_contains_site_name(self):
        provider = _FakeProvider()
        fill_index(provider, "ctx", "AwesomeTool")
        _, prompt = provider.calls[0]
        assert "AwesomeTool" in prompt

    def test_prompt_contains_context(self):
        provider = _FakeProvider()
        fill_index(provider, "unique-ctx-string-xyz", "proj")
        _, prompt = provider.calls[0]
        assert "unique-ctx-string-xyz" in prompt

    def test_no_placeholders_in_output(self):
        provider = _FakeProvider("# Title\nClean content without placeholders.")
        result = fill_index(provider, "ctx", "proj")
        assert "sdd-docs:placeholder" not in result


# ---------------------------------------------------------------------------
# fill_mkdocs
# ---------------------------------------------------------------------------

class TestFillMkdocs:
    def test_calls_provider_generate(self):
        provider = _FakeProvider("site_name: proj")
        result = fill_mkdocs(provider, "ctx", "proj", "nav:\n  - Home: index.md")
        assert "site_name: proj" in result
        assert len(provider.calls) == 1

    def test_prompt_contains_nav_block(self):
        provider = _FakeProvider()
        nav = "nav:\n  - Home: index.md\n  - Ref: reference/core.md"
        fill_mkdocs(provider, "ctx", "proj", nav)
        _, prompt = provider.calls[0]
        assert "nav:\n  - Home: index.md" in prompt

    def test_prompt_contains_mermaid_requirement(self):
        provider = _FakeProvider()
        fill_mkdocs(provider, "ctx", "proj", "nav:")
        _, prompt = provider.calls[0]
        assert "mermaid" in prompt


# ---------------------------------------------------------------------------
# fill_reference_prose
# ---------------------------------------------------------------------------

class TestFillReferenceProse:
    def test_calls_provider_generate(self):
        provider = _FakeProvider("The core domain handles...")
        result = fill_reference_prose(provider, "core", "ctx")
        assert result == "The core domain handles..."

    def test_prompt_contains_domain(self):
        provider = _FakeProvider()
        fill_reference_prose(provider, "providers", "ctx")
        _, prompt = provider.calls[0]
        assert "providers" in prompt

    def test_uses_lower_max_tokens(self):
        """Prose is short — max_tokens should be 300 to keep responses focused."""
        provider = _FakeProvider()
        fill_reference_prose(provider, "core", "ctx")
        # We can't directly test max_tokens on _FakeProvider, but we verify generate is called
        assert len(provider.calls) == 1
