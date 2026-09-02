# VDI Troubleshooting Commands

Run only the current test unless instructed otherwise. Paste the complete text output into `results.md` under the matching test number.

## Tests 001–006

Completed. See `results.md`.

Test 006 confirmed the user-local Codex installation and returned `codex-cli 0.152.1`.

---

## Test 007 — Persist Node.js and Codex on the User PATH

Run Test 007 first if you have not already done so. After opening a fresh PowerShell session, confirm:

```powershell
node --version
npm --version
codex --version
```

If those work, continue directly to Test 008.

---

## Test 008 — Discover Existing LiteLLM Proxy State

### Goal

Before changing any LiteLLM or Codex configuration, determine what is already present on the VDI and whether anything is currently listening on the expected local proxy port (`4000`).

This test is read-only. It does not start, stop, install, or reconfigure LiteLLM.

### PowerShell

```powershell
Write-Host "=== Port 4000 listener ==="
try {
    Get-NetTCPConnection -LocalPort 4000 -State Listen -ErrorAction Stop |
        Select-Object LocalAddress, LocalPort, State, OwningProcess
} catch {
    Write-Host "No listening TCP endpoint found on local port 4000."
}

Write-Host "`n=== Process owning port 4000, if any ==="
try {
    $listeners = @(Get-NetTCPConnection -LocalPort 4000 -State Listen -ErrorAction Stop)
    foreach ($listener in $listeners) {
        Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue |
            Select-Object Id, ProcessName, Path
    }
} catch {
    Write-Host "No process to report."
}

Write-Host "`n=== LiteLLM command discovery ==="
$litellm = Get-Command litellm -ErrorAction SilentlyContinue
if ($litellm) {
    Write-Host "litellm command: $($litellm.Source)"
    try { litellm --version } catch { Write-Host "litellm --version failed: $($_.Exception.Message)" }
} else {
    Write-Host "litellm command: NOT FOUND on PATH"
}

Write-Host "`n=== Likely LiteLLM files under user profile ==="
$roots = @(
    (Join-Path $HOME "litellm"),
    (Join-Path $HOME ".litellm"),
    (Join-Path $HOME "tools\litellm")
)
foreach ($root in $roots) {
    if (Test-Path $root) {
        Write-Host "FOUND: $root"
        Get-ChildItem $root -Force -ErrorAction SilentlyContinue |
            Select-Object -First 20 Name, FullName, Mode
    }
}

Write-Host "`n=== Local proxy HTTP probe ==="
try {
    $response = Invoke-WebRequest `
        -Uri "http://127.0.0.1:4000/health/liveliness" `
        -UseBasicParsing `
        -TimeoutSec 5
    Write-Host "HTTP status: $($response.StatusCode)"
    Write-Host "Body: $($response.Content)"
} catch {
    Write-Host "Proxy probe failed: $($_.Exception.Message)"
}
```

### Expected output

This should tell us one of three things:

1. LiteLLM is already running on port 4000.
2. LiteLLM/configuration exists but is not running.
3. There is no usable LiteLLM installation on this VDI yet.

Any of those outcomes is fine. The next step will be based on the actual state rather than reinstalling or overwriting anything unnecessarily.

### Important

Do **not** print environment variables, API keys, Azure endpoints containing secrets, bearer tokens, or configuration-file contents yet. We only want installation/process/path information.

### Safety

Read-only. No configuration or credentials are modified.
