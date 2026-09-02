# Test 009 — LiteLLM Azure Provider Using Resource-Root Endpoint

## Purpose

The direct Azure Responses API test succeeded using:

- Azure resource: `corestory-genai-sa`
- Azure v1 endpoint: `https://corestory-genai-sa.openai.azure.com/openai/v1`
- model/deployment identifier: `gpt-5.4`
- wire API: Responses

This proves the Azure resource, key, and `gpt-5.4` identifier are valid.

This test isolates LiteLLM's Azure provider configuration. It uses the resource-root endpoint and API-version form expected by the archived token-metering runbook, then tests LiteLLM's `/v1/responses` route before involving Codex.

Do not commit credentials or print the Azure key.

## 1. Stop the existing LiteLLM proxy

In the PowerShell window running LiteLLM, press:

```text
Ctrl+C
```

## 2. Set the Azure provider environment

In the PowerShell window that will run LiteLLM:

```powershell
$env:AZURE_API_BASE="https://corestory-genai-sa.openai.azure.com/"
$env:AZURE_API_VERSION="2025-04-01-preview"
```

The Azure key should already be available as `AZURE_API_KEY`. Verify the variables without printing credentials:

```powershell
Write-Host "AZURE_API_BASE = $env:AZURE_API_BASE"
Write-Host "AZURE_API_VERSION = $env:AZURE_API_VERSION"
Write-Host "AZURE_API_KEY set = $([bool]$env:AZURE_API_KEY)"
```

Expected shape:

```text
AZURE_API_BASE = https://corestory-genai-sa.openai.azure.com/
AZURE_API_VERSION = 2025-04-01-preview
AZURE_API_KEY set = True
```

If `AZURE_API_KEY set` is `False`, set it in this PowerShell session before continuing. Do not paste the value into this file.

## 3. Update `config.yaml`

Use this configuration for the test:

```yaml
model_list:
  - model_name: gpt-5.4
    litellm_params:
      model: azure/gpt-5.4
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
      api_version: os.environ/AZURE_API_VERSION
    model_info:
      base_model: azure/gpt-5.4

litellm_settings:
  callbacks: usage_logger.proxy_handler_instance
  drop_params: true
```

This test intentionally changes the Azure provider endpoint form from `/openai/v1` to the Azure resource root. Do not change the deployment/model identifier at the same time.

## 4. Start LiteLLM

From the token-metering directory, with the virtual environment active:

```powershell
litellm --config .\config.yaml --port 4000
```

Leave this window running.

Capture the relevant startup output below. Do not include credentials.

### Proxy startup result

```text
 .\set-env-vars.ps1
AZURE_API_BASE = https://corestory-genai-sa.openai.azure.com/
AZURE_API_VERSION = 2025-04-01-preview
AZURE_API_KEY set = True
(.venv) PS C:\Users\carys\token-metering> litellm --config .\config.yaml --port 4000
←[32mINFO←[0m:     Started server process [←[36m%d←[0m]
←[32mINFO←[0m:     Waiting for application startup.

   ██╗     ██╗████████╗███████╗██╗     ██╗     ███╗   ███╗
   ██║     ██║╚══██╔══╝██╔════╝██║     ██║     ████╗ ████║
   ██║     ██║   ██║   █████╗  ██║     ██║     ██╔████╔██║
   ██║     ██║   ██║   ██╔══╝  ██║     ██║     ██║╚██╔╝██║
   ███████╗██║   ██║   ███████╗███████╗███████╗██║ ╚═╝ ██║
   ╚══════╝╚═╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝     ╚═╝


←[1;37m#------------------------------------------------------------#←[0m
←[1;37m#                                                            #←[0m
←[1;37m#       'This feature doesn't meet my needs because...'       #←[0m
←[1;37m#        https://github.com/BerriAI/litellm/issues/new        #←[0m
←[1;37m#                                                            #←[0m
←[1;37m#------------------------------------------------------------#←[0m

 Thank you for using LiteLLM! - Krrish & Ishaan



←[1;31mGive Feedback / Get Help: https://github.com/BerriAI/litellm/issues/new←[0m


←[32mLiteLLM: Proxy initialized with Config, Set models:←[0m
←[32m    gpt-5.4←[0m
←[92m12:50:16 - LiteLLM:WARNING←[0m: utils.py:2898 - register_model: model=8b0a4659cf250fb2135b7940dee052bf2fc834d62511964ba0574efcad031c37 not in built-in cost map and no prefix/region variant matched; cache cost fields will default to 0. To track cache cost, add cache_creation_input_token_cost and cache_read_input_token_cost to model_info
←[32mINFO←[0m:     Application startup complete.
←[32mINFO←[0m:     Uvicorn running on ←[1m%s://%s:%d←[0m (Press CTRL+C to quit)
```

## 5. Test LiteLLM's Responses API route

Open a second PowerShell window and run:

```powershell
$body = @{
    model = "gpt-5.4"
    input = "Say hello in one sentence."
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
    -Uri "http://localhost:4000/v1/responses" `
    -Method Post `
    -ContentType "application/json" `
    -Headers @{ "Authorization" = "Bearer sk-local" } `
    -Body $body | ConvertTo-Json -Depth 20
```

Paste the complete response or error below.

### LiteLLM Responses result

```text
PASTE RESULT HERE
```

## 6. Check the token usage log

If the request succeeds, from the token-metering directory run:

```powershell
Get-Content .\token_usage.jsonl -Tail 2
```

Paste the output below.

### Token log result

```text
PASTE RESULT HERE
```

If the request fails, it is still useful to check whether the file exists, but do not treat a missing usage row as a separate failure: the callback is expected to log completed successful requests.

## Interpretation

- **Responses succeeds and token row is written:** LiteLLM → Azure GPT-5.4 and the usage logger are proven. Proceed to Codex → LiteLLM.
- **Responses succeeds but no token row appears:** Azure routing is fixed; troubleshoot only the custom usage callback/logger.
- **Azure returns 404:** compare LiteLLM's generated Azure request behavior with the already-successful direct Azure v1 control test before changing another variable.
- **400/parameter error:** Azure was reached. Preserve the full error and inspect which parameter or API behavior LiteLLM changed.
- **401/403:** verify that the LiteLLM process has the expected `AZURE_API_KEY` and that the endpoint/key pairing matches the successful direct Azure test.

## Result summary

After running the test, add a one-line summary here before committing:

```text
RESULT: PENDING
```
