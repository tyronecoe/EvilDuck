# Normal policy and permissions only; no automatic Start, bypass, install or networking.
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $PSScriptRoot 'WindowsCapture.cs') -ReferencedAssemblies System.Windows.Forms,System.Drawing
[EvilDuckCapture]::Run()
