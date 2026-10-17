# Run visibly from a normal PowerShell 5.1+ console; do not bypass execution policy.
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $PSScriptRoot 'WindowsSender.cs')
exit [EvilDuckLedSender]::Run()
