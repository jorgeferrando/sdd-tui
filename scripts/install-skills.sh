#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# SDD Skills installer for Claude Code (delegates to sdd-skills repo)
# ---------------------------------------------------------------------------

REPO_URL="https://github.com/jorgeferrando/sdd-skills"

echo "Downloading SDD skills from GitHub..."
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
git clone --depth=1 --quiet "$REPO_URL" "$TMP_DIR"

# Delegate to the installer from sdd-skills
bash "$TMP_DIR/install-skills.sh" "$@"
