# Test 013 — Codex CLI → LiteLLM → Azure GPT-5.4

## Purpose

Test 012 validated the metering layer for LiteLLM Responses API calls. This test adds Codex as the client and proves the complete path:

```text
Codex CLI
  → LiteLLM localhost:4000
  → Azure OpenAI GPT-5.4
  → token_usage.jsonl
```

This is an integration smoke test, not a benchmark. Use a trivial prompt and do not involve the customer codebase yet.

The test is successful if:

1. Codex uses the local LiteLLM provider.
2. LiteLLM receives a Responses API request.
3. Azure GPT-5.4 returns a valid answer.
4. `token_usage.jsonl` receives one or more rows from the Codex request with non-zero input/output usage.

Do not commit credentials, API keys, customer source, or sensitive prompt/response content.

## 1. Confirm Codex is available

Open a new PowerShell window and run:

```powershell
codex --version
```

Expected from the earlier installation test:

```text
codex-cli 0.152.1
```

### Codex version result

```text
codex-cli 0.152.1
```

## 2. Back up the existing Codex configuration

The Codex config file is expected at:

```text
%USERPROFILE%\.codex\config.toml
```

Run:

```powershell
$codexDir = Join-Path $env:USERPROFILE ".codex"
$configPath = Join-Path $codexDir "config.toml"

New-Item -ItemType Directory -Path $codexDir -Force | Out-Null

if (Test-Path $configPath) {
    Copy-Item $configPath "$configPath.pre-test013.bak" -Force
    Write-Host "Existing Codex config backed up: True"
} else {
    Write-Host "Existing Codex config backed up: False - no prior config existed"
}
```

Do not paste the contents of an existing customer Codex configuration into this document.

## 3. Configure Codex to use LiteLLM

For this test, replace `%USERPROFILE%\.codex\config.toml` with:

```toml
model = "gpt-5.4"
model_provider = "litellm"
model_reasoning_effort = "medium"

[model_providers.litellm]
name = "LiteLLM (local)"
base_url = "http://localhost:4000/v1"
env_key = "LITELLM_API_KEY"
wire_api = "responses"
```

This intentionally changes only the Codex provider. LiteLLM's Azure configuration should remain exactly as validated in Test 012.

## 4. Set the local LiteLLM client key

The local LiteLLM proxy does not currently require a production secret. Set the throwaway client value expected by the Codex provider:

```powershell
$env:LITELLM_API_KEY="sk-local"
Write-Host "LITELLM_API_KEY set = $([bool]$env:LITELLM_API_KEY)"
```

Expected:

```text
LITELLM_API_KEY set = True
```

Do not print the value itself.

## 5. Start LiteLLM with a dedicated run label

In the PowerShell window used to run LiteLLM, set:

```powershell
$env:RUN_LABEL="test-013-codex-litellm"
```

Keep the Azure environment and `config.yaml` exactly as they were for the successful Test 012.

Start the proxy:

```powershell
litellm --config .\config.yaml --port 4000
```

Leave this window running.

### LiteLLM startup result

```text
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
←[1;37m#           'I get frustrated when the product...'            #←[0m
←[1;37m#        https://github.com/BerriAI/litellm/issues/new        #←[0m
←[1;37m#                                                            #←[0m
←[1;37m#------------------------------------------------------------#←[0m

 Thank you for using LiteLLM! - Krrish & Ishaan



←[1;31mGive Feedback / Get Help: https://github.com/BerriAI/litellm/issues/new←[0m


←[32mLiteLLM: Proxy initialized with Config, Set models:←[0m
←[32m    gpt-5.4←[0m
←[92m15:24:41 - LiteLLM:WARNING←[0m: utils.py:2898 - register_model: model=8b0a4659cf250fb2135b7940dee052bf2fc834d62511964ba0574efcad031c37 not in built-in cost map and no prefix/region variant matched; cache cost fields will default to 0. To track cache cost, add cache_creation_input_token_cost and cache_read_input_token_cost to model_info
←[32mINFO←[0m:     Application startup complete.
←[32mINFO←[0m:     Uvicorn running on ←[1m%s://%s:%d←[0m (Press CTRL+C to quit)
```

## 6. Record the current token-log tail

Before running Codex, in a second PowerShell window from the token-metering directory:

```powershell
Get-Content .\token_usage.jsonl -Tail 3 -ErrorAction SilentlyContinue
```

This establishes the before state so the new Codex rows are easy to identify.

### Token log before Codex

```text
{"ts": "2026-09-02T19:25:16.086260+00:00", "run": "test-012-proxy-validation", "model": "gpt-5.4", "call_type": "aresponses", "latency_s": 1.173, "input_tokens": 12, "cached_input_tokens": 0, "uncached_input_tokens": 12, "output_tokens": 6, "reasoning_tokens": 0, "visible_output_tokens": 6, "total_tokens": 18}
```

## 7. Verify the non-interactive Codex command is available

Run:

```powershell
codex exec --help
```

We only need to confirm that the `exec` subcommand is available. Do not paste the full help output unless there is an error.

### `codex exec` availability

```text
PS C:\Users\carys\.codex> codex exec --help
Run Codex non-interactively

Usage: codex exec [OPTIONS] [PROMPT]
       codex exec [OPTIONS] <COMMAND> [ARGS]

Commands:
  resume  Resume a previous session by id or pick the most recent with --last
  fork    Fork a previous session by id into a new session
  review  Run a code review against the current repository
  help    Print this message or the help of the given subcommand(s)

Arguments:
  [PROMPT]
          Initial instructions for the agent. If not provided as an argument (or if `-` is used), instructions are read
          from stdin. If stdin is piped and a prompt is also provided, stdin is appended as a `<stdin>` block

Options:
  -c, --config <key=value>
          Override a configuration value that would otherwise be loaded from `~/.codex/config.toml`. Use a dotted path
          (`foo.bar.baz`) to override nested values. The `value` portion is parsed as TOML. If it fails to parse as
          TOML, the raw string is used as a literal.

          Examples: - `-c model="o3"` - `-c 'sandbox_permissions=["disk-full-read-access"]'` - `-c
          shell_environment_policy.inherit=all`

      --enable <FEATURE>
          Enable a feature (repeatable). Equivalent to `-c features.<name>=true`

      --disable <FEATURE>
          Disable a feature (repeatable). Equivalent to `-c features.<name>=false`

      --strict-config
          Error out when config.toml contains fields that are not recognized by this version of Codex

  -i, --image <FILE>...
          Optional image(s) to attach to the initial prompt

  -m, --model <MODEL>
          Model the agent should use

      --oss
          Use open-source provider

      --local-provider <OSS_PROVIDER>
          Specify which local provider to use (lmstudio or ollama). If not specified with --oss, will use config default
          or show selection

  -p, --profile <CONFIG_PROFILE_V2>
          Layer $CODEX_HOME/<name>.config.toml on top of the base user config

  -s, --sandbox <SANDBOX_MODE>
          Select the sandbox policy to use when executing model-generated shell commands

          [possible values: read-only, workspace-write, danger-full-access]

      --approve-for-me
          Route approval requests through automatic review using the workspace-write sandbox

      --dangerously-bypass-approvals-and-sandbox
          Skip all confirmation prompts and execute commands without sandboxing. EXTREMELY DANGEROUS. Intended solely
          for running in environments that are externally sandboxed

      --dangerously-bypass-hook-trust
          Run enabled hooks without requiring persisted hook trust for this invocation. DANGEROUS. Intended only for
          automation that already vets hook sources

  -C, --cd <DIR>
          Tell the agent to use the specified directory as its working root

      --add-dir <DIR>
          Additional directories that should be writable alongside the primary workspace

      --thread-source <SOURCE>
          Source classification for newly created or forked threads

      --skip-git-repo-check
          Allow running Codex outside a Git repository

      --ephemeral
          Run without persisting session files to disk

      --ignore-user-config
          Do not load `$CODEX_HOME/config.toml`; auth still uses `CODEX_HOME`

      --ignore-rules
          Do not load user or project execpolicy `.rules` files

      --output-schema <FILE>
          Path to a JSON Schema file describing the model's final response shape

      --color <COLOR>
          Specifies color settings for use in the output

          [default: auto]
          [possible values: always, never, auto]

      --json
          Print events to stdout as JSONL

  -o, --output-last-message <FILE>
          Specifies file where the last message from the agent should be written

  -h, --help
          Print help (see a summary with '-h')

  -V, --version
          Print version
```

## 8. Send one trivial Codex request

Run:

```powershell
codex exec "Reply with exactly: CODEX_LITELLM_OK"
```

Do not run this from the customer source repository. A neutral directory such as the token-metering folder is preferred for this connectivity test.

### Codex result

```text
PS C:\Users\carys\.codex> codex exec "Reply with exactly: CODEX_LITELLM_OK"
Not inside a trusted directory and --skip-git-repo-check was not specified.
```

A successful result should include the requested marker:

```text
CODEX_LITELLM_OK
```

Codex may emit additional CLI status information. Preserve enough of the output to show which model/provider was selected if Codex displays it.

## 9. Capture the LiteLLM token log

Immediately after the Codex request completes:

```powershell
Get-Content .\token_usage.jsonl -Tail 10
```

Paste the new rows below.

### Token log after Codex

```text
PASTE RESULT HERE
```

For a successful Codex path, look for rows with:

```text
run       = test-013-codex-litellm
model     = gpt-5.4
call_type = aresponses
```

There may be more than one model request for a single Codex command. That is useful information, not a failure. Preserve all rows generated by this one command.

## 10. Check the LiteLLM console

Capture the relevant request line(s) from the LiteLLM window. We want to confirm that the Codex request reached the Responses endpoint and did not silently bypass the proxy.

### LiteLLM request result

```text
PASTE RELEVANT REQUEST/STATUS LINES HERE
```

## Validation criteria

This test passes when all of the following are true:

```text
Codex command succeeds
Codex returns CODEX_LITELLM_OK
LiteLLM receives the request
Azure GPT-5.4 answers successfully
One or more new JSONL rows are written
New JSONL rows contain non-zero input/output/total token counts
Run label is test-013-codex-litellm
```

## Interpretation

- **Codex succeeds and JSONL rows appear:** the complete Codex → LiteLLM → Azure → metering path is proven. We can move to a controlled agent task next.
- **Codex succeeds but no JSONL rows appear:** verify Codex did not bypass the custom provider and inspect the LiteLLM console before changing the logger.
- **Codex cannot connect to localhost:4000:** verify LiteLLM is still listening and that `base_url` is exactly `http://localhost:4000/v1`.
- **Codex reports authentication failure against LiteLLM:** verify `LITELLM_API_KEY` exists in the same PowerShell process launching Codex. Do not change Azure credentials.
- **LiteLLM receives the request but Azure fails:** preserve the proxy error. Test 012 remains the known-good control, so do not change multiple variables at once.
- **Codex rejects `wire_api = "responses"` or the provider config:** preserve the exact Codex error before changing `config.toml`.

## Restore guidance

Do not restore the prior Codex configuration until the test result has been reviewed. If restoration becomes necessary later and a backup exists:

```powershell
$configPath = Join-Path (Join-Path $env:USERPROFILE ".codex") "config.toml"
Copy-Item "$configPath.pre-test013.bak" $configPath -Force
```

## Result summary

```text
RESULT: PENDING
```

Commit this file with the results before moving to a real agent task or customer-code benchmark.
