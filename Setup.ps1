#Requires -Version 5.1
<#
.SYNOPSIS
Install uv (Tools stage), or set up the locked environment and map (Configure stage).
.DESCRIPTION
Run Tools first, then reopen PowerShell. Complete Battle.net installation and
first launch before Configure. Configure is repeatable and never starts SC2.
Local paths are saved only after preflight succeeds. No administrator shell needed.
#>
[CmdletBinding()]
param(
    [ValidateSet('Tools', 'Configure')][string]$Stage = 'Configure',
    [string]$Sc2Path,
    [string]$MapFile
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RepoRoot = $PSScriptRoot
$SettingsPath = Join-Path $RepoRoot '.local/windows.json'
$ExitCode = 0

function Invoke-Uv {
    & uv @args
    if ($LASTEXITCODE -ne 0) { throw "uv failed (exit $LASTEXITCODE). Fix the error above and rerun setup." }
}

function Test-OfficialMap([string]$Path) {
    $Data = [IO.File]::ReadAllBytes($Path)
    $Header = [Text.Encoding]::ASCII.GetBytes("blob $($Data.Length)" + [char]0)
    $Hash = [Security.Cryptography.SHA1]::Create()
    try {
        $null = $Hash.TransformBlock($Header, 0, $Header.Length, $Header, 0)
        $null = $Hash.TransformFinalBlock($Data, 0, $Data.Length)
        return ([BitConverter]::ToString($Hash.Hash).Replace('-', '').ToLowerInvariant() -eq
            '42694de3201acea2269813c2f1bf6703af29c703')
    }
    finally { $Hash.Dispose() }
}

try {
    if ($env:OS -ne 'Windows_NT') { throw 'Run this script in native Windows PowerShell, not WSL.' }
    if ($Stage -eq 'Tools') {
        if (Get-Command uv -ErrorAction SilentlyContinue) {
            Invoke-Uv --version
            Write-Host 'Tools ready. Complete Battle.net first launch, then run Setup.ps1.'
        }
        else {
            if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
                throw 'WinGet unavailable. Install uv from https://docs.astral.sh/uv/getting-started/installation/ then reopen PowerShell.'
            }
            & winget install --id astral-sh.uv -e --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity
            if ($LASTEXITCODE -notin @(0, 3010)) { throw "uv installation failed (WinGet exit $LASTEXITCODE)." }
            Write-Host 'Tools installed. STOP: close/reopen PowerShell for PATH changes; reboot Windows if the installer requests it.'
            Write-Host 'After Battle.net first launch, continue with Setup.ps1 (Configure stage).'
            $ExitCode = 3010
        }
    }
    else {
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'uv unavailable. Run Setup.ps1 -Stage Tools, then reopen PowerShell.' }
        # Resolve supplied paths before changing directory: relative paths belong to the caller.
        if ($Sc2Path) { $Sc2Path = (Resolve-Path -LiteralPath $Sc2Path).ProviderPath }
        if ($MapFile) { $MapFile = (Resolve-Path -LiteralPath $MapFile).ProviderPath }
        if (Test-Path -LiteralPath $SettingsPath) {
            $Saved = Get-Content -LiteralPath $SettingsPath -Raw | ConvertFrom-Json
            if ($Saved.schema_version -ne 1) { throw 'Unsupported .local/windows.json schema.' }
            if (-not $Sc2Path) { $Sc2Path = $Saved.sc2_path }
            if (-not $MapFile) { $MapFile = $Saved.map_file }
        }
        Push-Location -LiteralPath $RepoRoot
        try {
            Invoke-Uv sync --locked --python 3.12
            Invoke-Uv run --locked --no-sync sc2-assistant --check-config --config config/assistant.example.json
            foreach ($Directory in @('maps', 'logs', 'replays', '.local')) {
                $null = New-Item -ItemType Directory -Force -Path $Directory
            }
            $DefaultMap = Join-Path $RepoRoot 'maps/BelShirVestigeLE.SC2Map'
            if (-not $MapFile) { $MapFile = $DefaultMap }
            if ($MapFile -eq $DefaultMap) {
                if (Test-Path -LiteralPath $MapFile) {
                    if (-not (Test-OfficialMap $MapFile)) {
                        throw "Map hash mismatch: $MapFile. Move the file aside and rerun; it was not overwritten."
                    }
                }
                else {
                    $Url = "https://raw.githubusercontent.com/Blizzard/s2client-api/614acc00abb5355e4c94a1b0279b46e9d845b7ce/maps/Ladder/(2)Bel'ShirVestigeLE%20(Void).SC2Map"
                    $Temporary = Join-Path $RepoRoot ('.local/map-' + [guid]::NewGuid().ToString() + '.tmp')
                    try {
                        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
                        Invoke-WebRequest -Uri $Url -OutFile $Temporary -UseBasicParsing
                        if (-not (Test-OfficialMap $Temporary)) { throw 'Downloaded map hash mismatch; download rejected.' }
                        Move-Item -LiteralPath $Temporary -Destination $MapFile
                    }
                    finally {
                        if (Test-Path -LiteralPath $Temporary) { Remove-Item -LiteralPath $Temporary }
                    }
                }
            }
            $DoctorArgs = @('run', '--locked', '--no-sync', 'sc2-assistant', '--doctor', '--map-file', $MapFile)
            if ($Sc2Path) { $DoctorArgs += @('--sc2-path', $Sc2Path) }
            $Doctor = (Invoke-Uv @DoctorArgs) -join "`n" | ConvertFrom-Json
            if (-not $Doctor.preflight_ok) { throw 'SC2/map preflight did not pass.' }
            $Settings = [ordered]@{
                schema_version = 1
                sc2_path = $Doctor.installation.root
                map_file = $MapFile
            }
            $Settings | ConvertTo-Json | Set-Content -LiteralPath "$SettingsPath.tmp" -Encoding UTF8
            Move-Item -LiteralPath "$SettingsPath.tmp" -Destination $SettingsPath -Force
            Write-Host 'Setup complete. Paths saved locally. SC2 has not been started.'
            Write-Host 'Next: .\Start.ps1 -Probe, then .\Start.ps1 -StartPaused -Difficulty VeryEasy'
        }
        finally { Pop-Location }
    }
}
catch {
    Write-Error -Message $_.Exception.Message -ErrorAction Continue
    $ExitCode = 1
}
exit $ExitCode
