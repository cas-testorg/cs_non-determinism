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
