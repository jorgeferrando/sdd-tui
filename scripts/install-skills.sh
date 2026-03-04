#!/usr/bin/env bash
set -euo pipefail

# Resolve the skills/ directory relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/../skills"

# When piped through curl, BASH_SOURCE[0] may be empty — fallback to a temp clone
if [[ ! -d "$SKILLS_SRC" ]]; then
    echo "Downloading SDD skills from GitHub..."
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TMP_DIR"' EXIT
    git clone --depth=1 --quiet https://github.com/jorgeferrando/sdd-tui "$TMP_DIR"
    SKILLS_SRC="$TMP_DIR/skills"
fi

# Determine destination
if [[ "${1:-}" == "--global" ]]; then
    DEST="$HOME/.claude/skills"
elif [[ "${1:-}" == "--local" ]]; then
    DEST="$(pwd)/.claude/skills"
else
    echo "Install SDD skills for Claude Code"
    echo ""
    echo "  [1] Global (~/.claude/skills/) — available in all projects"
    echo "  [2] Project-local (.claude/skills/) — current project only"
    echo ""
    read -rp "Choice [1/2]: " choice
    case "$choice" in
        1) DEST="$HOME/.claude/skills" ;;
        2) DEST="$(pwd)/.claude/skills" ;;
        *) echo "Invalid choice. Use 1 or 2."; exit 1 ;;
    esac
fi

mkdir -p "$DEST"
installed=0
skipped=0

for skill_dir in "$SKILLS_SRC"/sdd-*/; do
    skill_name="$(basename "$skill_dir")"
    target="$DEST/$skill_name"
    if [[ -d "$target" ]]; then
        echo "  skip  $skill_name (already exists — delete to reinstall)"
        ((skipped+=1))
    else
        cp -r "$skill_dir" "$target"
        echo "  ✓     $skill_name"
        ((installed+=1))
    fi
done

echo ""
echo "Installed: $installed  Skipped: $skipped"
echo "Destination: $DEST"
echo ""
echo "Restart Claude Code to load the new skills."
echo "Then use /sdd-init to get started."
