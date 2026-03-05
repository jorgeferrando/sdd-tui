#!/usr/bin/env bash
# sdd-env-scan — detects available environment for /sdd-init onboarding
# Output: structured text, one entry per line, format: category:name:value
# Usage: bash scripts/sdd-env-scan.sh

set -euo pipefail

# --- Runtimes ---
check_runtime() {
    local name="$1"
    local version_cmd="${2:---version}"
    if command -v "$name" &>/dev/null; then
        local version
        version=$("$name" $version_cmd 2>&1 | head -1 | tr -d '\n') || version="unknown"
        echo "runtime:${name}:${version}"
    else
        echo "runtime:${name}:missing"
    fi
}

check_runtime node "--version"
check_runtime python3 "--version"
check_runtime php "--version"
check_runtime ruby "--version"
check_runtime go "version"
check_runtime rustc "--version"
check_runtime java "-version"

# --- CLI Tools ---
check_tool() {
    local name="$1"
    if command -v "$name" &>/dev/null; then
        echo "tool:${name}:available"
    else
        echo "tool:${name}:missing"
    fi
}

check_tool git
check_tool gh
check_tool docker
check_tool uv
check_tool bun
check_tool composer
check_tool make
check_tool curl
check_tool jq

# --- Package managers / lock files ---
check_file() {
    local path="$1"
    if [ -f "$path" ]; then
        echo "file:${path}:found"
    else
        echo "file:${path}:missing"
    fi
}

check_file "package.json"
check_file "package-lock.json"
check_file "yarn.lock"
check_file "bun.lockb"
check_file "pyproject.toml"
check_file "requirements.txt"
check_file "Pipfile"
check_file "composer.json"
check_file "go.mod"
check_file "Cargo.toml"
check_file "Gemfile"
check_file "pom.xml"
check_file "build.gradle"

# --- Source directories ---
check_dir() {
    local path="$1"
    if [ -d "$path" ]; then
        echo "dir:${path}:found"
    else
        echo "dir:${path}:missing"
    fi
}

check_dir "src"
check_dir "lib"
check_dir "app"
check_dir "pkg"
check_dir "cmd"
check_dir "tests"
check_dir "test"
check_dir "spec"
check_dir ".github"
check_dir ".gitlab"

# --- Docker containers (if docker available and running) ---
if command -v docker &>/dev/null; then
    if docker info &>/dev/null 2>&1; then
        containers=$(docker ps --format "{{.Names}}" 2>/dev/null) || containers=""
        if [ -n "$containers" ]; then
            while IFS= read -r name; do
                echo "container:${name}:running"
            done <<< "$containers"
        else
            echo "container:none:no containers running"
        fi
    else
        echo "container:docker:daemon not running"
    fi
else
    echo "container:docker:not installed"
fi

# --- openspec state ---
if [ -d "openspec" ]; then
    echo "openspec:dir:found"
else
    echo "openspec:dir:missing"
fi

if [ -d "openspec/steering" ]; then
    echo "openspec:steering:found"
else
    echo "openspec:steering:missing"
fi

if [ -f "openspec/steering/conventions.md" ]; then
    echo "openspec:conventions:found"
else
    echo "openspec:conventions:missing"
fi

if [ -f "openspec/steering/project-rules.md" ]; then
    echo "openspec:project-rules:found"
else
    echo "openspec:project-rules:missing"
fi

if [ -f "openspec/config.yaml" ]; then
    echo "openspec:config:found"
else
    echo "openspec:config:missing"
fi

# --- git state ---
if command -v git &>/dev/null && git rev-parse --git-dir &>/dev/null 2>&1; then
    echo "git:repo:found"
    branch=$(git branch --show-current 2>/dev/null) || branch="unknown"
    echo "git:branch:${branch}"
else
    echo "git:repo:missing"
fi

# --- CLAUDE.md ---
if [ -f "CLAUDE.md" ]; then
    echo "claude:CLAUDE.md:found"
else
    echo "claude:CLAUDE.md:missing"
fi

if [ -f ".claude/CLAUDE.md" ]; then
    echo "claude:.claude/CLAUDE.md:found"
else
    echo "claude:.claude/CLAUDE.md:missing"
fi
