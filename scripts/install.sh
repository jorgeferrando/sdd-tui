#!/usr/bin/env bash
# install.sh — installs sdd-tui and SDD skills on Linux (and macOS without Homebrew)
#
# Usage:
#   bash scripts/install.sh              # interactive
#   bash scripts/install.sh --skip-skills
#
# Pipe-friendly (without cloning):
#   curl -fsSL https://raw.githubusercontent.com/jorgeferrando/sdd-tui/main/scripts/install.sh | bash

set -euo pipefail

SKIP_SKILLS=0
for arg in "$@"; do
    [[ "$arg" == "--skip-skills" ]] && SKIP_SKILLS=1
done

# ---------------------------------------------------------------------------
# 1. Detect package manager
# ---------------------------------------------------------------------------

PKG_MANAGER=""

if command -v uv &>/dev/null; then
    PKG_MANAGER="uv"
elif command -v pipx &>/dev/null; then
    PKG_MANAGER="pipx"
elif command -v pip3 &>/dev/null; then
    PKG_MANAGER="pip3"
elif command -v pip &>/dev/null; then
    PKG_MANAGER="pip"
fi

if [[ -z "$PKG_MANAGER" ]]; then
    echo ""
    echo "Error: no Python package manager found (uv, pipx, pip)."
    echo ""
    echo "Install uv (recommended):"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Or install pipx:"
    echo "  python3 -m pip install --user pipx"
    echo ""
    exit 1
fi

echo "Using: $PKG_MANAGER"

# ---------------------------------------------------------------------------
# 2. Install sdd-tui
# ---------------------------------------------------------------------------

REPO_URL="git+https://github.com/jorgeferrando/sdd-tui"

echo "Installing sdd-tui..."
case "$PKG_MANAGER" in
    uv)   uv tool install "$REPO_URL" ;;
    pipx) pipx install "$REPO_URL" ;;
    pip3) pip3 install --user "$REPO_URL" ;;
    pip)  pip install --user "$REPO_URL" ;;
esac

echo "sdd-tui installed."

# ---------------------------------------------------------------------------
# 3. Install skills (unless --skip-skills)
# ---------------------------------------------------------------------------

if [[ "$SKIP_SKILLS" -eq 1 ]]; then
    echo ""
    echo "Skipping skills install (--skip-skills)."
    echo "Run 'sdd-setup' later to install SDD skills."
else
    echo ""
    if command -v sdd-setup &>/dev/null; then
        sdd-setup --global
    else
        # sdd-setup not in PATH yet — try via uv tool run or uvx
        if command -v uvx &>/dev/null; then
            uvx --from sdd-tui sdd-setup --global
        else
            echo "Note: 'sdd-setup' not found in PATH."
            echo "      Restart your shell and run: sdd-setup --global"
        fi
    fi
fi
