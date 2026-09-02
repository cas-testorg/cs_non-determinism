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

Completed successfully. Node.js `v22.23.2` and npm `10.9.8` are working from a user-local install under `%USERPROFILE%\tools\nodejs`.

---

## Test 006 — Install Codex CLI in User Space

### Goal

Install the official OpenAI Codex CLI without administrator privileges or machine-wide changes.

OpenAI's current documented CLI installation remains:

```text
npm i -g @openai/codex
```

Because this VDI uses a portable Node.js installation, this test explicitly directs global npm packages to a user-owned directory.

### Important before running

Run this in the **same PowerShell window** used for Test 005 if possible. If that window was closed, the script below will rediscover the portable Node.js directory and add it to the current session automatically.

### PowerShell

```powershell
$ErrorActionPreference = "Stop"

Write-Host "=== Locate portable Node.js ==="
$nodeDir = Get-ChildItem (Join-Path $HOME "tools\nodejs") -Directory -Filter "node-v*-win-x64" |
    Sort-Object Name -Descending |
    Select-Object -First 1 -ExpandProperty FullName

if (-not $nodeDir) {
    throw "Portable Node.js installation was not found under $HOME\tools\nodejs."
}

$env:PATH = "$nodeDir;$env:PATH"
Write-Host "Node directory: $nodeDir"
node --version
npm --version

Write-Host "`n=== Configure user-local npm global directory ==="
$npmGlobal = Join-Path $HOME "tools\npm-global"
New-Item -ItemType Directory -Path $npmGlobal -Force | Out-Null
npm config set prefix "$npmGlobal"
$env:PATH = "$npmGlobal;$nodeDir;$env:PATH"
Write-Host "npm global prefix: $(npm config get prefix)"

Write-Host "`n=== Install Codex CLI ==="
npm install -g @openai/codex

Write-Host "`n=== Verify Codex CLI ==="
$codexCmd = Join-Path $npmGlobal "codex.cmd"
if (-not (Test-Path $codexCmd)) {
    throw "Codex command was not found at $codexCmd"
}

Write-Host "Codex path: $codexCmd"
& $codexCmd --version
```

### Expected output

We want to see:

- Node.js and npm versions again,
- npm global prefix under `%USERPROFILE%\tools\npm-global`,
- successful installation of `@openai/codex`, and
- a valid `codex --version` result.

### Stop here

Do **not** sign in to Codex or configure LiteLLM yet. We only want to prove that the CLI itself installs and launches.

Once this succeeds, the next test will make Node/npm/Codex convenient to launch in a fresh PowerShell session and then we can begin the LiteLLM routing test.

### Safety

- No administrator privileges are required.
- No machine-wide configuration is changed.
- No OpenAI, Azure, LiteLLM, or customer credentials should be entered during this test.
