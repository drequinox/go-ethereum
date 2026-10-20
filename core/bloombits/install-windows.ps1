# Installs the DASG skill and agents for GitHub Copilot Chat in VS Code (Windows).
# Run from this folder:  powershell -ExecutionPolicy Bypass -File .\install-windows.ps1

$ErrorActionPreference = "Stop"
$src    = Split-Path -Parent $MyInvocation.MyCommand.Path
$skills = Join-Path $env:USERPROFILE ".claude\skills"
$agents = Join-Path $env:USERPROFILE ".claude\agents"

New-Item -ItemType Directory -Force -Path $skills | Out-Null
New-Item -ItemType Directory -Force -Path $agents | Out-Null

Copy-Item -Recurse -Force (Join-Path $src "skills\dasg-protocol-security-review") $skills
Copy-Item -Force (Join-Path $src "agents\*.md") $agents

Write-Host "Installed:"
Get-ChildItem -Recurse (Join-Path $skills "dasg-protocol-security-review") -File | ForEach-Object { Write-Host "  $($_.FullName)" }
Get-ChildItem (Join-Path $agents "dasg-*.md") | ForEach-Object { Write-Host "  $($_.FullName)" }
Write-Host ""
Write-Host "Next: in VS Code run 'Developer: Reload Window', then type / in Copilot Chat (Agent mode)."
