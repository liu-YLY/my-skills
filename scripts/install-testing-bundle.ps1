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
foreach ($required in @("testing-bundle", "test-case-engineer", "bug-analyzer", "test-strategy-engineer", "performance-test-engineer", "state-machine-test-engineer", "change-impact-analyzer", "test-data-generator")) {
    if ($required -notin $BundleSkills) { throw "Missing required skill: $required" }
}
foreach ($resource in @("convert_docs.py", "requirements.txt")) {
    $resourcePath = Join-Path $SkillsSource "test-case-engineer/scripts/$resource"
    if (-not (Test-Path -LiteralPath $resourcePath -PathType Leaf)) {
        throw "Missing conversion resource: $resourcePath"
    }
}
function Assert-RuntimeResources([string]$Root) {
    $prefix = [IO.Path]::GetFullPath($Root) + [IO.Path]::DirectorySeparatorChar
    $dataResources = @(
        "scripts/run_data.py", "scripts/requirements.txt", "schemas/profile.schema.json", "schemas/report.schema.json",
        "scripts/engine/__init__.py", "scripts/engine/common.py", "scripts/engine/profile.py",
        "scripts/engine/generators.py", "scripts/engine/relations.py", "scripts/engine/validator.py",
        "scripts/engine/negative.py", "scripts/engine/exporters.py", "scripts/engine/pipeline.py", "scripts/engine/runner.py"
    )
    foreach ($resource in $dataResources) {
        $path = Join-Path $Root "test-data-generator/$resource"
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing data generation resource: $path" }
    }
    foreach ($resource in @("convert_docs.py", "requirements.txt")) {
        $path = Join-Path $Root "test-case-engineer/scripts/$resource"
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing conversion resource: $path" }
    }
    foreach ($document in Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "*.md") {
        foreach ($link in [regex]::Matches((Get-Content -LiteralPath $document.FullName -Raw), '\[[^\]]*\]\(([^)\s]+)\)')) {
            $relative = ($link.Groups[1].Value -split '#', 2)[0]
            if (-not $relative -or $relative -match '^[a-zA-Z][a-zA-Z0-9+.-]*:|[{}*]') { continue }
            if ($relative -notmatch '[/\\.]') { continue } # syntax-example placeholders
            $resolved = [IO.Path]::GetFullPath((Join-Path $document.DirectoryName $relative))
            if (-not $resolved.StartsWith($prefix) -or -not (Test-Path -LiteralPath $resolved)) {
                throw "Missing portable runtime reference: $($document.FullName) -> $relative"
            }
        }
    }
}
Assert-RuntimeResources $SkillsSource

# Copy and validate the portable layout before touching existing installations.
$stage = Join-Path ([IO.Path]::GetTempPath()) ("testing-skills-" + [guid]::NewGuid().ToString("N"))
$payload = Join-Path $stage "payload"
$backup = Join-Path $stage "backup"
$installed = @()
$replaced = @()
$keepBackup = $false
try {
    New-Item -ItemType Directory -Path $payload, $backup -Force | Out-Null
    foreach ($skill in $BundleSkills) {
        Copy-Item (Join-Path $SkillsSource $skill) (Join-Path $payload $skill) -Recurse -Force
    }
    Assert-RuntimeResources $payload
    if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null }
    foreach ($skill in $BundleSkills) {
        $dst = Join-Path $TargetDir $skill
        if (Test-Path -LiteralPath $dst) {
            Move-Item -LiteralPath $dst -Destination (Join-Path $backup $skill)
            $replaced += $skill
        }
        Move-Item -LiteralPath (Join-Path $payload $skill) -Destination $dst
        $installed += $skill
        Write-Host "  installed $skill"
    }
} catch {
    $keepBackup = $true # Keep recoverable old files if rollback itself fails.
    foreach ($skill in $installed) { Remove-Item -LiteralPath (Join-Path $TargetDir $skill) -Recurse -Force }
    foreach ($skill in $replaced) { Move-Item -LiteralPath (Join-Path $backup $skill) -Destination (Join-Path $TargetDir $skill) }
    $keepBackup = $false
    throw
} finally {
    if (-not $keepBackup -and (Test-Path -LiteralPath $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force }
}

Write-Host ""
Write-Host "Done. Restart the runtime to activate testing-bundle." -ForegroundColor Cyan
Write-Host "Skill files copied; Python dependencies and MCP servers require separate installation. Missing MCP uses independent mode." -ForegroundColor DarkGray
Write-Host ""
Write-Host "For other runtimes, use -TargetDir, e.g.:" -ForegroundColor DarkGray
Write-Host "  Cursor: -TargetDir `"$ProfileDir\.cursor\skills`"" -ForegroundColor DarkGray
Write-Host "  Codex:   -TargetDir `"$ProfileDir\.codex\skills`"" -ForegroundColor DarkGray
Write-Host "  TRAE:    -TargetDir `"$ProfileDir\.trae-cn\skills`" (path to be confirmed)" -ForegroundColor DarkGray
