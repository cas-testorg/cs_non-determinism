# Direct Azure Responses API Test

Use this test to bypass LiteLLM and verify the Azure endpoint and `gpt-5.4` deployment/model directly.

Do not commit credentials. Set the Azure key only in the client PowerShell session.

## Known values

```text
Base URL: https://corestory-genai-sa.openai.azure.com/openai/v1
Model/deployment candidate: gpt-5.4
Wire API: responses
```

## Run on the client VDI

Confirm the key is already set without printing it:

```powershell
Write-Host "Azure key set: $([bool]$env:AZURE_OPENAI_API_KEY)"
```

Then run:

```powershell
$base = "https://corestory-genai-sa.openai.azure.com/openai/v1"

$body = @{
    model = "gpt-5.4"
    input = "Say hello in one sentence."
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "$base/responses" `
    -Method Post `
    -ContentType "application/json" `
    -Headers @{ "api-key" = $env:AZURE_OPENAI_API_KEY } `
    -Body $body | ConvertTo-Json -Depth 20
```

## Capture the result

Paste the complete command output below, making sure no credential appears in the output, then commit this file back to the branch.

### Result

```text
PASTE OUTPUT HERE
```

## Interpretation

- Success: endpoint, key, and `gpt-5.4` identifier are valid; return to the LiteLLM configuration.
- HTTP 404: endpoint path or Azure deployment/model identifier is likely wrong.
- HTTP 401/403: endpoint/key pairing or authorization is likely wrong.
- HTTP 400 or another parameter error: Azure was reached; inspect the returned API error before changing LiteLLM.
