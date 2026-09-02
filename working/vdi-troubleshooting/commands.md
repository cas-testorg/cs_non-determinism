# VDI Troubleshooting Commands

Run only the current test unless instructed otherwise. Paste the complete text output into `results.md` under the matching test number.

## Tests 001–006

Completed. See `results.md`.

Test 006 confirmed the user-local Codex installation and returned `codex-cli 0.152.1`.

---

## Test 007 — Persist Node.js and Codex on the User PATH

### Goal

Make the portable Node.js and Codex installations available from a **new PowerShell session** without administrator privileges.

This modifies only the current user's `PATH`, not the machine-wide `PATH`.

### PowerShell

```powershell
$ErrorActionPreference = "Stop"

$nodeDir = Get-ChildItem (Join-Path $HOME "tools\nodejs") -Directory -Filter "node-v*-win-x64" |
    Sort-Object Name -Descending |
    Select-Object -First 1 -ExpandProperty FullName

$npmGlobal = Join-Path $HOME "tools\npm-global"

if (-not $nodeDir) { throw "Portable Node.js directory was not found." }
if (-not (Test-Path (Join-Path $npmGlobal "codex.cmd"))) { throw "Codex CLI was not found in $npmGlobal." }

Write-Host "=== Paths to persist ==="
Write-Host "Node:  $nodeDir"
Write-Host "Codex: $npmGlobal"

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$parts = @()
if ($userPath) {
    $parts = @($userPath -split ';' | Where-Object { $_ -and $_.Trim() })
}

foreach ($entry in @($nodeDir, $npmGlobal)) {
    if ($parts -notcontains $entry) {
        $parts += $entry
    }
}

$newUserPath = $parts -join ';'
[Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")

Write-Host "`n=== User PATH updated ==="
Write-Host "Node path present:  $($parts -contains $nodeDir)"
Write-Host "Codex path present: $($parts -contains $npmGlobal)"

Write-Host "`n=== Current-session verification ==="
$env:PATH = "$npmGlobal;$nodeDir;$env:PATH"
node --version
npm --version
codex --version
```

### Expected output

We want all three version checks to succeed and both `... path present` values to be `True`.

### Final manual check

After the script succeeds:

1. Close that PowerShell window.
2. Open a completely new PowerShell window.
3. Run:

```powershell
node --version
npm --version
codex --version
```

Paste those three results into `results.md` too.

### Stop here

Do not sign in to Codex yet. Once a fresh PowerShell session can launch Codex, the installation layer is complete and the next test will focus on the existing LiteLLM proxy and its Azure route.

### Safety

This changes only the current user's `PATH`. It requires no administrator privileges and does not store or display credentials.
