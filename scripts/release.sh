#!/usr/bin/env bash
# release.sh — Full release automation for sdd-tui
#
# Usage: scripts/release.sh <version>
# Example: scripts/release.sh 0.2.0
#
# Requires: git, uv, gh, curl, python3

set -euo pipefail

VERSION="${1:-}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

step()  { echo "→ $*"; }
ok()    { echo "✓ $*"; }
fail()  { echo "✗ $*" >&2; exit 1; }

REPO_ROOT="$(git rev-parse --show-toplevel)"
OPENSPEC="$REPO_ROOT/openspec/config.yaml"

_read_config() {
    local key="$1"
    local section="$2"
    awk "/^${section}:/{f=1} f && /^  ${key}:/{print \$2; exit}" "$OPENSPEC" 2>/dev/null || echo ""
}

# ---------------------------------------------------------------------------
# Step 0: Validate
# ---------------------------------------------------------------------------

step "Validating arguments..."
if [[ -z "$VERSION" ]]; then
    fail "Usage: scripts/release.sh <version>  (e.g. 0.2.0)"
fi
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    fail "Version must be semver X.Y.Z — got: $VERSION"
fi
ok "Version $VERSION"

step "Checking required tools..."
for tool in git uv gh curl; do
    if ! command -v "$tool" &>/dev/null; then
        if [[ "$tool" == "gh" ]]; then
            fail "gh (GitHub CLI) not found. Install: https://cli.github.com/"
        fi
        fail "$tool not found"
    fi
done
ok "Tools available: git, uv, gh, curl"

step "Checking tag v$VERSION does not already exist..."
if git tag | grep -q "^v${VERSION}$"; then
    fail "Tag v$VERSION already exists locally"
fi
if gh release view "v$VERSION" &>/dev/null 2>&1; then
    fail "GitHub release v$VERSION already exists"
fi
ok "Tag v$VERSION is available"

# ---------------------------------------------------------------------------
# Step 1: Tests
# ---------------------------------------------------------------------------

step "Running tests..."
if ! uv run pytest --tb=short -q; then
    fail "Tests failed — aborting release"
fi
ok "Tests passed"

# ---------------------------------------------------------------------------
# Step 2: Working tree check
# ---------------------------------------------------------------------------

step "Checking working tree is clean..."
DIRTY=$(git status --porcelain | grep -v "^??" | grep -v "openspec/" | grep -v ".claude/" || true)
if [[ -n "$DIRTY" ]]; then
    echo "$DIRTY"
    fail "Working tree dirty — commit or stash changes before releasing"
fi
ok "Working tree clean"

# ---------------------------------------------------------------------------
# Step 3: Bump version in pyproject.toml
# ---------------------------------------------------------------------------

step "Bumping version to $VERSION in pyproject.toml..."
PYPROJECT="$REPO_ROOT/pyproject.toml"
if ! grep -q 'version = ' "$PYPROJECT"; then
    fail "Could not find 'version = ' in pyproject.toml"
fi
sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" "$PYPROJECT"
rm -f "$PYPROJECT.bak"
git add "$PYPROJECT"
git commit -m "[release] Bump version to $VERSION

Co-Authored-By: release.sh <noreply>"
ok "Bumped to $VERSION"

# ---------------------------------------------------------------------------
# Step 4: Regenerate CHANGELOG.md
# ---------------------------------------------------------------------------

CHANGELOG_SOURCE=$(_read_config changelog_source release_workflow)
CHANGELOG_SOURCE="${CHANGELOG_SOURCE:-openspec}"

if [[ "$CHANGELOG_SOURCE" == "openspec" ]]; then
    step "Regenerating CHANGELOG.md..."
    uv run python "$REPO_ROOT/scripts/changelog.py"
    git add "$REPO_ROOT/CHANGELOG.md"
    git commit -m "[release] Update CHANGELOG.md for v$VERSION

Co-Authored-By: release.sh <noreply>"
    ok "CHANGELOG.md updated"
else
    step "Skipping CHANGELOG.md (changelog_source=$CHANGELOG_SOURCE)"
fi

# ---------------------------------------------------------------------------
# Step 5: Tag and push
# ---------------------------------------------------------------------------

step "Creating tag v$VERSION..."
git tag -a "v$VERSION" -m "v$VERSION"
ok "Tag v$VERSION created"

step "Pushing main + tag..."
git push origin main --tags
ok "Pushed to origin"

# ---------------------------------------------------------------------------
# Step 6: GitHub Release
# ---------------------------------------------------------------------------

step "Extracting release notes..."
RELEASE_NOTES=$(uv run python "$REPO_ROOT/scripts/changelog.py" --version "$VERSION" 2>/dev/null || echo "")
if [[ -z "$RELEASE_NOTES" ]]; then
    RELEASE_NOTES="Release v$VERSION"
fi

step "Creating GitHub Release v$VERSION..."
gh release create "v$VERSION" \
    --title "v$VERSION" \
    --notes "$RELEASE_NOTES"
ok "GitHub Release v$VERSION created"

# ---------------------------------------------------------------------------
# Step 7: Update Homebrew formula (optional)
# ---------------------------------------------------------------------------

HOMEBREW_FORMULA=$(_read_config homebrew_formula release_workflow)
if [[ -n "$HOMEBREW_FORMULA" && "$HOMEBREW_FORMULA" != "null" && "$HOMEBREW_FORMULA" != "none" ]]; then
    FORMULA_PATH="$REPO_ROOT/$HOMEBREW_FORMULA"
    if [[ -f "$FORMULA_PATH" ]]; then
        step "Computing SHA256 for release tarball..."
        TARBALL_URL="https://github.com/jorgeferrando/sdd-tui/archive/refs/tags/v${VERSION}.tar.gz"
        SHA256=$(curl -sL "$TARBALL_URL" | sha256sum | awk '{print $1}')
        if [[ -z "$SHA256" ]]; then
            fail "Could not compute SHA256 for $TARBALL_URL"
        fi
        ok "SHA256: $SHA256"

        step "Updating $HOMEBREW_FORMULA..."
        sed -i.bak "s|url \".*\"|url \"$TARBALL_URL\"|" "$FORMULA_PATH"
        sed -i.bak "s|sha256 \".*\"|sha256 \"$SHA256\"|" "$FORMULA_PATH"
        rm -f "$FORMULA_PATH.bak"
        git add "$FORMULA_PATH"
        git commit -m "[release] Update Homebrew formula for v$VERSION

Co-Authored-By: release.sh <noreply>"
        git push origin main
        ok "Homebrew formula updated"
    else
        step "Formula file not found ($FORMULA_PATH) — skipping"
    fi
else
    step "No Homebrew formula configured — skipping"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ok "Release v$VERSION complete"
echo "   https://github.com/jorgeferrando/sdd-tui/releases/tag/v$VERSION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
