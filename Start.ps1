#Requires -Version 5.1
<#
.SYNOPSIS
Start the local SC2 economy assistant using paths saved by Setup.ps1.
.DESCRIPTION
Defaults to a real-time match against Medium Terran. Use -Probe to test only the
API or -StartPaused on the first match. No installs/downloads are performed.
Relative path overrides resolve from the caller's directory. The script can be
invoked from any directory and runs the application from the repository root.
#>
[CmdletBinding()]
param(
    [switch]$Probe,
    [switch]$CheckOnly,
    [switch]$StartPaused,
    [ValidateSet('VeryEasy', 'Easy', 'Medium', 'MediumHard', 'Hard', 'Harder', 'VeryHard', 'CheatVision', 'CheatMoney', 'CheatInsane')]
    [string]$Difficulty = 'Medium',
    [ValidateSet('Terran', 'Protoss', 'Zerg', 'Random')][string]$Opponent = 'Terran',
    [ValidateRange(0, 65535)][int]$AttachPort = 0,
    [string]$Sc2Version = 'latest',
    [string]$Sc2Path,
    [string]$MapFile,
    [string]$ConfigFile
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RepoRoot = $PSScriptRoot
$ExitCode = 0
try {
    if ($env:OS -ne 'Windows_NT') { throw 'Run this script in native Windows PowerShell, not WSL.' }
    if ($Probe -and $CheckOnly) { throw 'Choose either -Probe or -CheckOnly.' }
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'uv unavailable. Run Setup.ps1 -Stage Tools and reopen PowerShell.' }
    $SettingsPath = Join-Path $RepoRoot '.local/windows.json'
    if (-not (Test-Path -LiteralPath $SettingsPath)) { throw 'Setup is incomplete. Run Setup.ps1 first.' }
    if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot '.venv/Scripts/python.exe'))) {
        throw 'Python environment missing. Rerun Setup.ps1.'
    }
    $Saved = Get-Content -LiteralPath $SettingsPath -Raw | ConvertFrom-Json
    if ($Saved.schema_version -ne 1) { throw 'Unsupported .local/windows.json schema. Rerun Setup.ps1.' }
    if ($Sc2Path) { $Sc2Path = (Resolve-Path -LiteralPath $Sc2Path).ProviderPath }
    else { $Sc2Path = $Saved.sc2_path }
    if ($MapFile) { $MapFile = (Resolve-Path -LiteralPath $MapFile).ProviderPath }
    else { $MapFile = $Saved.map_file }
    if ($ConfigFile) { $ConfigFile = (Resolve-Path -LiteralPath $ConfigFile).ProviderPath }
    else { $ConfigFile = Join-Path $RepoRoot 'config/assistant.example.json' }
    $LaunchArgs = @('run', '--locked', '--no-sync', 'sc2-assistant', '--sc2-path', $Sc2Path,
        '--sc2-version', $Sc2Version, '--config', $ConfigFile)
    if ($Probe) { $LaunchArgs += '--probe' }
    else {
        $LaunchArgs += @('--map-file', $MapFile)
        if ($CheckOnly) { $LaunchArgs += '--doctor' }
        else { $LaunchArgs += @('--difficulty', $Difficulty, '--opponent', $Opponent) }
    }
    if ($StartPaused) { $LaunchArgs += '--start-paused' }
    if ($AttachPort) { $LaunchArgs += @('--attach-port', [string]$AttachPort) }
    Push-Location -LiteralPath $RepoRoot
    try {
        & uv @LaunchArgs
        $ExitCode = $LASTEXITCODE
        if ($ExitCode -ne 0) { Write-Error "SC2 assistant failed (exit $ExitCode). See logs/ and docs/windows-troubleshooting.md." -ErrorAction Continue }
    }
    finally { Pop-Location }
}
catch {
    Write-Error -Message $_.Exception.Message -ErrorAction Continue
    $ExitCode = 1
}
exit $ExitCode
