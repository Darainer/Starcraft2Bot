#Requires -Version 5.1
[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$Report,
    [switch]$State,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Command
)
$ErrorActionPreference = 'Stop'
if (-not $Report) {
    $latest = Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'logs') -Filter 'runtime-*.json' |
        Where-Object { $_.Name -match '^runtime-\d{8}-\d{6}-\d+\.json$' } |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $latest) { throw 'No runtime report found. Start the assistant first.' }
    $Report = $latest.FullName
}
$controlArgs = @('-m', 'source.control_cli', '--report', $Report)
if ($State) { $controlArgs += '--state' }
if ($Command) { $controlArgs += $Command }
Push-Location -LiteralPath $PSScriptRoot
try {
    & (Join-Path $PSScriptRoot '.venv\Scripts\python.exe') @controlArgs
    if ($LASTEXITCODE -ne 0) { throw "Control command failed (exit $LASTEXITCODE)." }
}
finally { Pop-Location }
