# VDI Troubleshooting Commands

Run only the current test unless instructed otherwise. Paste the complete text output into `results.md` under the matching test number.

## Test 001 — Environment Discovery

Completed. See `results.md`.

---

## Test 002 — Verify Node.js Install Path

Completed. See `results.md`.

---

## Test 003 — Diagnose winget Node.js Discovery

Completed. `winget` itself is present, but both package discovery operations terminated with exit code `-1073741819` rather than returning package metadata.

---

## Test 004 — Check Direct Node.js Download Connectivity

Completed. The VDI can resolve `nodejs.org` and reach the Node.js distribution endpoint over HTTPS with HTTP 200.

---

## Test 005 — Install Node.js LTS in User Space

### Goal

Install Node.js without admin rights and without using the failing `winget` client. This uses the official Node.js Windows x64 ZIP distribution and extracts it under the current user's profile.

This test does **not** modify machine-wide configuration. It only updates `PATH` for the current PowerShell session so we can verify Node.js and npm before deciding whether to persist anything.

### PowerShell

```powershell
$ErrorActionPreference = "Stop"

$baseUrl = "https://nodejs.org/dist/latest-v22.x/"
$installRoot = Join-Path $HOME "tools\nodejs"
$tempZip = Join-Path $env:TEMP "node-lts-win-x64.zip"

Write-Host "=== Discover latest Node.js v22 x64 ZIP ==="
$index = Invoke-WebRequest -Uri $baseUrl -UseBasicParsing -TimeoutSec 30
$match = [regex]::Match($index.Content, 'node-v[0-9.]+-win-x64\.zip')

if (-not $match.Success) {
    throw "Could not find the Windows x64 ZIP filename in the Node.js distribution index."
}

$fileName = $match.Value
$downloadUrl = $baseUrl + $fileName
Write-Host "Package: $fileName"
Write-Host "Source:  $downloadUrl"
Write-Host "Target:  $installRoot"

Write-Host "`n=== Download ==="
Invoke-WebRequest -Uri $downloadUrl -OutFile $tempZip -UseBasicParsing -TimeoutSec 120
Get-Item $tempZip | Select-Object FullName, Length

Write-Host "`n=== Extract ==="
if (Test-Path $installRoot) {
    Remove-Item $installRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $installRoot -Force | Out-Null
Expand-Archive -Path $tempZip -DestinationPath $installRoot -Force

$nodeDir = Get-ChildItem $installRoot -Directory | Select-Object -First 1 -ExpandProperty FullName
if (-not $nodeDir) {
    throw "Node.js extraction directory was not found."
}

Write-Host "Node directory: $nodeDir"

Write-Host "`n=== Add Node.js to this PowerShell session only ==="
$env:PATH = "$nodeDir;$env:PATH"

Write-Host "`n=== Verify ==="
Write-Host "node path: $((Get-Command node).Source)"
Write-Host "npm path:  $((Get-Command npm).Source)"
node --version
npm --version
```

### Expected output

We want to see:

- the discovered official `node-v...-win-x64.zip` filename,
- a successful download and extraction under your user profile,
- a valid `node --version`, and
- a valid `npm --version`.

### Important

The PATH change is **session-only**. If you close PowerShell after this test, `node` and `npm` will not automatically be available in the next terminal yet. That is intentional; we will persist the user-level PATH only after this succeeds.

### Safety

- No administrator privileges are required.
- Nothing is installed machine-wide.
- The download comes directly from `https://nodejs.org/`.
- No credentials or customer-sensitive information should appear in the output.
