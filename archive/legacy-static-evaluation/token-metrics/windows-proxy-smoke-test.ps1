# Windows -> Linux LiteLLM proxy smoke test
#
# Purpose:
#   1. Verify the SSH-local-forwarded LiteLLM port is reachable on Windows.
#   2. Send one Responses API request through the proxy.
#   3. Print the response so the Linux-side token_usage.jsonl can be checked.
#
# Prerequisite:
#   Keep an SSH tunnel open in a separate PowerShell window, for example:
#   ssh -L 4000:127.0.0.1:4000 carys@us01odcvde73961

$ErrorActionPreference = 'Stop'

Write-Host 'Testing localhost:4000...'
$test = Test-NetConnection localhost -Port 4000

if (-not $test.TcpTestSucceeded) {
    Write-Error 'Port 4000 is not reachable. Verify the SSH tunnel is open and LiteLLM is listening on Linux.'
    exit 1
}

Write-Host 'Port 4000 is reachable.'
Write-Host 'Sending Responses API smoke test...'

$body = @{
    model = 'gpt-5.4'
    input = 'Reply with exactly: windows proxy test successful'
    reasoning = @{
        effort = 'medium'
    }
} | ConvertTo-Json -Depth 5

$response = Invoke-RestMethod `
    -Method Post `
    -Uri 'http://localhost:4000/v1/responses' `
    -Headers @{ Authorization = 'Bearer sk-local' } `
    -ContentType 'application/json' `
    -Body $body

Write-Host ''
Write-Host 'Proxy request succeeded.'
$response | ConvertTo-Json -Depth 12

Write-Host ''
Write-Host 'Next: on the Linux VM run:'
Write-Host 'tail -n 2 "$HOME/token-metering/token_usage.jsonl"'
