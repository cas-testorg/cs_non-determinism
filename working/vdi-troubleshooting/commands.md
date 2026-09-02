# VDI Troubleshooting Commands

Run only the current test unless instructed otherwise. Paste the complete text output into `results.md` under the matching test number.

## Test 001 — Environment Discovery

### Goal

Determine which installation and diagnostic paths are available on the Windows 11 VDI before changing the environment.

### PowerShell

```powershell
Write-Host "=== OS ==="
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber

Write-Host "`n=== Package / Runtime Availability ==="
$commands = @("winget", "python", "py", "git", "node", "npm", "codex")
foreach ($cmd in $commands) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) {
        Write-Host "$cmd : FOUND -> $($found.Source)"
    } else {
        Write-Host "$cmd : NOT FOUND"
    }
}

Write-Host "`n=== Versions ==="
if (Get-Command winget -ErrorAction SilentlyContinue) { winget --version }
if (Get-Command python -ErrorAction SilentlyContinue) { python --version }
if (Get-Command py -ErrorAction SilentlyContinue) { py --version }
if (Get-Command git -ErrorAction SilentlyContinue) { git --version }
if (Get-Command node -ErrorAction SilentlyContinue) { node --version }
if (Get-Command npm -ErrorAction SilentlyContinue) { npm --version }
if (Get-Command codex -ErrorAction SilentlyContinue) { codex --version }
```

### Expected output

A short inventory showing whether `winget`, Python, Git, Node/npm, and Codex are available, plus versions where present.

### Safety

This test is read-only. It installs nothing and should not display credentials.

---

## Test 002 — Verify Node.js Install Path

### Goal

Confirm that Windows Package Manager can see the official Node.js LTS package before we install anything. Codex CLI is distributed through npm, so Node.js/npm is the only missing prerequisite we need to address first.

### What Test 001 established

- `winget` is available.
- Git is installed.
- Node.js and npm are not installed.
- Codex CLI is not installed.
- The `python.exe` entry is only the Microsoft Store/App Execution Alias; there is no usable Python runtime at that path.

### PowerShell

```powershell
Write-Host "=== winget source status ==="
winget source list

Write-Host "`n=== Node.js LTS package lookup ==="
winget show --id OpenJS.NodeJS.LTS --exact
```

### Expected output

The second command should display the Node.js LTS package metadata, including package ID and available version.

### Do not install yet

This test is read-only. If the package lookup succeeds, stop here and paste the complete output into `results.md` under `Test 002`.

### Safety

Do not paste credentials, tokens, Azure endpoint secrets, or customer-sensitive information into GitHub.

---

## Test 003 — Diagnose winget Node.js Discovery

### Goal

Test 002 showed the winget sources but did not return Node.js LTS package metadata. Determine whether the package is discoverable through the configured `winget` source and capture winget's exit code/error text explicitly.

### PowerShell

```powershell
Write-Host "=== winget version ==="
winget --version

Write-Host "`n=== Search configured winget source for Node.js ==="
winget search --source winget nodejs
Write-Host "search exit code: $LASTEXITCODE"

Write-Host "`n=== Exact Node.js LTS lookup against winget source ==="
winget show --source winget --id OpenJS.NodeJS.LTS --exact --accept-source-agreements
Write-Host "show exit code: $LASTEXITCODE"
```

### Expected output

We need either:

- a row/package record for `OpenJS.NodeJS.LTS`, or
- an explicit winget error/exit code explaining why the package cannot be resolved.

### Do not install yet

This test is read-only. Do not run `winget install` yet.

### Safety

Do not paste credentials, tokens, Azure endpoint secrets, or customer-sensitive information into GitHub.
