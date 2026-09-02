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
PS C:\Users\carys\token-metering> .\test-azure-connection.ps1
{
    "id":  "resp_0aae1fcdb63ef8a3006a984b31ce9c8197a4320b8ab6360882",
    "object":  "response",
    "created_at":  1788365617,
    "status":  "completed",
    "background":  false,
    "completed_at":  1788365618,
    "content_filters":  [
                            {
                                "blocked":  false,
                                "source_type":  "prompt",
                                "content_filter_raw":  [

                                                       ],
                                "content_filter_results":  {
                                                               "hate":  {
                                                                            "filtered":  false,
                                                                            "severity":  "safe"
                                                                        },
                                                               "sexual":  {
                                                                              "filtered":  false,
                                                                              "severity":  "safe"
                                                                          },
                                                               "violence":  {
                                                                                "filtered":  false,
                                                                                "severity":  "safe"
                                                                            },
                                                               "self_harm":  {
                                                                                 "filtered":  false,
                                                                                 "severity":  "safe"
                                                                             },
                                                               "jailbreak":  {
                                                                                 "detected":  false,
                                                                                 "filtered":  false
                                                                             }
                                                           },
                                "content_filter_offsets":  {
                                                               "start_offset":  0,
                                                               "end_offset":  858,
                                                               "check_offset":  0
                                                           }
                            }
                        ],
    "error":  null,
    "frequency_penalty":  0.0,
    "incomplete_details":  null,
    "instructions":  null,
    "max_output_tokens":  null,
    "max_tool_calls":  null,
    "model":  "gpt-5.4",
    "moderation":  null,
    "output":  [
                   {
                       "id":  "msg_0aae1fcdb63ef8a3006a984b322f0c8197ab09440755917289",
                       "type":  "message",
                       "status":  "completed",
                       "content":  [
                                       {
                                           "type":  "output_text",
                                           "annotations":  [

                                                           ],
                                           "logprobs":  [

                                                        ],
                                           "text":  "Hello!"
                                       }
                                   ],
                       "phase":  "final_answer",
                       "role":  "assistant"
                   }
               ],
    "parallel_tool_calls":  true,
    "presence_penalty":  0.0,
    "previous_response_id":  null,
    "prompt_cache_key":  null,
    "prompt_cache_retention":  "in_memory",
    "reasoning":  {
                      "context":  "current_turn",
                      "effort":  "none",
                      "mode":  "standard",
                      "summary":  null
                  },
    "safety_identifier":  null,
    "service_tier":  "default",
    "store":  true,
    "temperature":  1.0,
    "text":  {
                 "format":  {
                                "type":  "text"
                            },
                 "verbosity":  "medium"
             },
    "tool_choice":  "auto",
    "tool_usage":  {
                       "image_gen":  {
                                         "input_tokens":  0,
                                         "input_tokens_details":  {
                                                                      "image_tokens":  0,
                                                                      "text_tokens":  0
                                                                  },
                                         "output_tokens":  0,
                                         "output_tokens_details":  {
                                                                       "image_tokens":  0,
                                                                       "text_tokens":  0
                                                                   },
                                         "total_tokens":  0
                                     },
                       "web_search":  {
                                          "num_requests":  0
                                      }
                   },
    "tools":  [

              ],
    "top_logprobs":  0,
    "top_p":  0.98,
    "truncation":  "disabled",
    "usage":  {
                  "input_tokens":  12,
                  "input_tokens_details":  {
                                               "cache_write_tokens":  0,
                                               "cached_tokens":  0
                                           },
                  "output_tokens":  6,
                  "output_tokens_details":  {
                                                "reasoning_tokens":  0
                                            },
                  "total_tokens":  18
              },
    "user":  null,
    "metadata":  {

                 }
}
```

## Interpretation

- Success: endpoint, key, and `gpt-5.4` identifier are valid; return to the LiteLLM configuration.
- HTTP 404: endpoint path or Azure deployment/model identifier is likely wrong.
- HTTP 401/403: endpoint/key pairing or authorization is likely wrong.
- HTTP 400 or another parameter error: Azure was reached; inspect the returned API error before changing LiteLLM.
