#Requires -Version 5.1
<#
.SYNOPSIS
    Installs sdd-tui and SDD skills on Windows.

.DESCRIPTION
    Detects uv, pipx, or pip and installs sdd-tui using the first available.
    Then runs sdd-setup --global to install SDD skills for Claude Code.

.PARAMETER SkipSkills
    If specified, skips the skills installation step.

.EXAMPLE
    .\Install-SddTui.ps1

.EXAMPLE
    .\Install-SddTui.ps1 -SkipSkills
#>
[CmdletBinding()]
param(
    [switch]$SkipSkills
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoUrl = "git+https://github.com/jorgeferrando/sdd-tui"

# ---------------------------------------------------------------------------
# 1. Detect package manager
# ---------------------------------------------------------------------------

$PkgManager = $null

if (Get-Command uv -ErrorAction SilentlyContinue) {
    $PkgManager = "uv"
} elseif (Get-Command pipx -ErrorAction SilentlyContinue) {
    $PkgManager = "pipx"
} elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
    $PkgManager = "pip3"
} elseif (Get-Command pip -ErrorAction SilentlyContinue) {
    $PkgManager = "pip"
}

if ($null -eq $PkgManager) {
    Write-Host ""
    Write-Host "Error: no Python package manager found (uv, pipx, pip)." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install uv (recommended):"
    Write-Host "  powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`""
    Write-Host ""
    Write-Host "Or install pipx:"
    Write-Host "  python -m pip install --user pipx"
    Write-Host ""
    exit 1
}

Write-Host "Using: $PkgManager"

# ---------------------------------------------------------------------------
# 2. Install sdd-tui
# ---------------------------------------------------------------------------

Write-Host "Installing sdd-tui..."

switch ($PkgManager) {
    "uv"   { uv tool install $RepoUrl }
    "pipx" { pipx install $RepoUrl }
    "pip3" { pip3 install --user $RepoUrl }
    "pip"  { pip install --user $RepoUrl }
}

Write-Host "sdd-tui installed."

# ---------------------------------------------------------------------------
# 3. Install skills (unless -SkipSkills)
# ---------------------------------------------------------------------------

if ($SkipSkills) {
    Write-Host ""
    Write-Host "Skipping skills install (-SkipSkills)."
    Write-Host "Run 'sdd-setup' later to install SDD skills."
} else {
    Write-Host ""
    if (Get-Command sdd-setup -ErrorAction SilentlyContinue) {
        sdd-setup --global
    } else {
        Write-Host "Note: 'sdd-setup' not found in PATH." -ForegroundColor Yellow
        Write-Host "      Restart your shell and run: sdd-setup --global"
    }
}
