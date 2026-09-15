<#
.SYNOPSIS
    Install all testing skills to a runtime skills directory

.DESCRIPTION
    Discover all skills under plugins/testing/skills, validate resources,
    then install specialist skills before the testing-bundle router.

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
$BundleSkills = @(Get-ChildItem -LiteralPath $SkillsSource -Directory |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") } |
    Sort-Object @{Expression = { $_.Name -eq "testing-bundle" }}, Name |
    ForEach-Object { $_.Name })

$ProfileDir = [Environment]::GetFolderPath("UserProfile")
if (-not $TargetDir) {
    $TargetDir = Join-Path $ProfileDir ".claude\skills"
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
Write-Host "Install testing-bundle ($($BundleSkills.Count) skills) -> $TargetDir" -ForegroundColor Green
foreach ($required in @("testing-bundle", "test-case-engineer", "bug-analyzer")) {
    if ($required -notin $BundleSkills) { throw "Missing required skill: $required" }
}
foreach ($resource in @("convert_docs.py", "requirements.txt")) {
    $resourcePath = Join-Path $SkillsSource "test-case-engineer/scripts/$resource"
    if (-not (Test-Path -LiteralPath $resourcePath -PathType Leaf)) {
        throw "Missing conversion resource: $resourcePath"
    }
}
# Validate runtime references before replacing any installed skill.
$SourcePrefix = [IO.Path]::GetFullPath($SkillsSource) + [IO.Path]::DirectorySeparatorChar
foreach ($document in Get-ChildItem -LiteralPath $SkillsSource -Recurse -File -Filter "*.md") {
    if ($document.Name -in @("README.md", "CHANGELOG.md") -or $document.FullName -match '[/\\]docs[/\\]') { continue }
    foreach ($link in [regex]::Matches((Get-Content -LiteralPath $document.FullName -Raw), '\[[^\]]*\]\(([^)\s]+)\)')) {
        $relative = ($link.Groups[1].Value -split '#', 2)[0]
        if (-not $relative -or $relative -match '^[a-zA-Z][a-zA-Z0-9+.-]*:|^/|[{}*]') { continue }
        $resolved = [IO.Path]::GetFullPath((Join-Path $document.DirectoryName $relative))
        if ($resolved.StartsWith($SourcePrefix) -and -not (Test-Path -LiteralPath $resolved)) {
            throw "Missing runtime reference: $($document.FullName) -> $relative"
        }
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
Write-Host "  Cursor: -TargetDir `"$ProfileDir\.cursor\skills`"" -ForegroundColor DarkGray
Write-Host "  Codex:   -TargetDir `"$ProfileDir\.codex\skills`"" -ForegroundColor DarkGray
Write-Host "  TRAE:    -TargetDir `"$ProfileDir\.trae-cn\skills`" (path to be confirmed)" -ForegroundColor DarkGray
