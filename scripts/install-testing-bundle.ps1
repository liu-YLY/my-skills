<#
.SYNOPSIS
    Install testing-bundle (test-case-engineer + bug-analyzer + testing-bundle) to a runtime skills directory

.DESCRIPTION
    testing-bundle is a meta skill with no concrete capability. It must be installed
    together with its two sub-skills to work. This script copies the three skill
    directories to the target runtime's skills folder.

    Source layout (flat under skills/, runtime-compatible):
      skills/testing-bundle/      # router entry
      skills/test-case-engineer/  # forward test-case generation
      skills/bug-analyzer/        # backward root-cause analysis

.PARAMETER TargetDir
    Target skills directory. Defaults to ~\.claude\skills (Claude Code).
    Other runtimes:
      Cursor: ~\.cursor\skills
      Codex:  ~\.codex\skills
      TRAE:   ~\.trae-cn\skills (path to be confirmed)

.PARAMETER Uninstall
    Remove the installed testing-bundle skills from the target directory

.EXAMPLE
    .\install-testing-bundle.ps1
    # Install to Claude Code (~\.claude\skills)

.EXAMPLE
    .\install-testing-bundle.ps1 -TargetDir "C:\Users\me\.cursor\skills"
    # Install to Cursor

.EXAMPLE
    .\install-testing-bundle.ps1 -Uninstall
    # Uninstall from the default target
#>

param(
    [string]$TargetDir = "",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# Locate project root (script lives at <root>/scripts/install-testing-bundle.ps1)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$SkillsSource = Join-Path $ProjectRoot "plugins\testing\skills"

# Install order: depended-upon sub-skills first, bundle entry last
$BundleSkills = @("test-case-engineer", "bug-analyzer", "testing-bundle")

if (-not $TargetDir) {
    $TargetDir = Join-Path $env:USERPROFILE ".claude\skills"
}

if ($Uninstall) {
    Write-Host "Uninstall testing-bundle <- $TargetDir" -ForegroundColor Yellow
    foreach ($skill in $BundleSkills) {
        $dst = Join-Path $TargetDir $skill
        if (Test-Path $dst) {
            Remove-Item $dst -Recurse -Force
            Write-Host "  removed $skill"
        } else {
            Write-Host "  skipped (not found) $skill" -ForegroundColor DarkGray
        }
    }
    Write-Host "Done." -ForegroundColor Green
    exit 0
}

# Pre-install validation
Write-Host "Install testing-bundle (3 skills) -> $TargetDir" -ForegroundColor Green
foreach ($skill in $BundleSkills) {
    $src = Join-Path $SkillsSource $skill
    if (-not (Test-Path $src)) {
        Write-Host "  source skill not found: $src" -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    Write-Host "  created target dir: $TargetDir" -ForegroundColor DarkGray
}

foreach ($skill in $BundleSkills) {
    $src = Join-Path $SkillsSource $skill
    $dst = Join-Path $TargetDir $skill
    if (Test-Path $dst) {
        Remove-Item $dst -Recurse -Force
        Write-Host "  overwrote old version $skill" -ForegroundColor DarkGray
    }
    Copy-Item $src $dst -Recurse -Force
    Write-Host "  installed $skill"
}

Write-Host ""
Write-Host "Done. Restart the runtime to activate testing-bundle." -ForegroundColor Cyan
Write-Host ""
Write-Host "For other runtimes, use -TargetDir, e.g.:" -ForegroundColor DarkGray
Write-Host "  Cursor: -TargetDir `"$env:USERPROFILE\.cursor\skills`"" -ForegroundColor DarkGray
Write-Host "  Codex:   -TargetDir `"$env:USERPROFILE\.codex\skills`"" -ForegroundColor DarkGray
Write-Host "  TRAE:    -TargetDir `"$env:USERPROFILE\.trae-cn\skills`" (path to be confirmed)" -ForegroundColor DarkGray
