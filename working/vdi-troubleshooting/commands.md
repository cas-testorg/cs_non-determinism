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

### Goal

Determine whether the VDI can reach the official Node.js distribution site without relying on `winget`. This is read-only and downloads nothing.

If this succeeds, we can consider a user-local Node.js installation path and bypass the failing `winget` client entirely.

### PowerShell

```powershell
Write-Host "=== Node.js distribution endpoint ==="
try {
    $response = Invoke-WebRequest `
        -Uri "https://nodejs.org/dist/latest-v22.x/" `
        -Method Head `
        -UseBasicParsing `
        -TimeoutSec 20

    Write-Host "HTTP status: $($response.StatusCode)"
    Write-Host "Final URI: $($response.BaseResponse.ResponseUri.AbsoluteUri)"
} catch {
    Write-Host "REQUEST FAILED"
    Write-Host "Exception type: $($_.Exception.GetType().FullName)"
    Write-Host "Message: $($_.Exception.Message)"

    if ($_.Exception.Response) {
        try { Write-Host "HTTP status: $([int]$_.Exception.Response.StatusCode)" } catch {}
    }
}

Write-Host "`n=== TLS / DNS basics ==="
try {
    Resolve-DnsName nodejs.org -ErrorAction Stop |
        Select-Object -First 4 Name, Type, IPAddress
} catch {
    Write-Host "DNS FAILED: $($_.Exception.Message)"
}
```

### Expected output

Ideally:

- an HTTP `200` response from `nodejs.org`, and
- successful DNS resolution.

A failure is also useful because it will tell us whether outbound access, TLS, DNS, or another VDI restriction is blocking the direct-install path.

### Do not install yet

This test downloads and installs nothing. Stop after capturing the output.

### Safety

No credentials or customer-sensitive information should appear in this output.
