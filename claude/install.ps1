<#
    Install Claude configs from this repo into ~/.claude via directory junctions.
    Junctions work without admin/developer mode on Windows and write through, so
    editing a skill while working updates the repo files (then commit & push).

    Usage:  pwsh -File claude/install.ps1
#>

$ErrorActionPreference = 'Stop'

$repoSkills = Join-Path $PSScriptRoot 'skills'
$claudeDir  = Join-Path $env:USERPROFILE '.claude'
$dstSkills  = Join-Path $claudeDir 'skills'

if (-not (Test-Path $repoSkills)) {
    throw "Cannot find $repoSkills - run this from the ai-configs repo."
}

New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null

if (Test-Path $dstSkills) {
    $item = Get-Item $dstSkills -Force
    $isLink = $item.LinkType -ne $null
    if ($isLink) {
        Write-Host "skills junction already exists -> $($item.Target). Re-creating."
        Remove-Item $dstSkills -Force
    } else {
        throw "$dstSkills already exists as a real folder. Move/merge its contents into $repoSkills first, then re-run."
    }
}

New-Item -ItemType Junction -Path $dstSkills -Target $repoSkills | Out-Null
Write-Host "Linked $dstSkills  ->  $repoSkills"
Write-Host "Installed skills:"
Get-ChildItem $dstSkills -Directory | ForEach-Object { Write-Host "  - $($_.Name)" }
