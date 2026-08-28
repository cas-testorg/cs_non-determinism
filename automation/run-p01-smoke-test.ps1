param(
    [string]$SourceRoot = (Get-Location).Path,
    [string]$CoreStoryMcp = "corestory",
    [string]$AgentCommand = "agent",
    [string]$Model = "gpt-5.4-high",
    [string]$OutputRoot = ".\results\p01-smoke"
)

$ErrorActionPreference = "Stop"

function Invoke-CursorAgent {
    param(
        [Parameter(Mandatory=$true)][string]$Prompt,
        [Parameter(Mandatory=$true)][string]$OutputFile
    )

    Write-Host "Running Cursor agent with model '$Model' -> $OutputFile"
    $output = & $AgentCommand -p $Prompt --model $Model --mode=ask --output-format text 2>&1
    $exitCode = $LASTEXITCODE
    $output | Set-Content -Path $OutputFile -Encoding UTF8

    if ($exitCode -ne 0) {
        throw "Cursor agent exited with code $exitCode. See $OutputFile"
    }

    return ($output -join [Environment]::NewLine)
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$promptPath = Join-Path $repoRoot "test-case-2-corestory\prompts\01-uninitialized-indeterminate-state.md"
$validatorPath = Join-Path $repoRoot "validation\independent-source-validation.md"

if (-not (Test-Path $promptPath)) { throw "P01 prompt not found: $promptPath" }
if (-not (Test-Path $validatorPath)) { throw "Validation template not found: $validatorPath" }
if (-not (Get-Command $AgentCommand -ErrorAction SilentlyContinue)) { throw "Cursor CLI command '$AgentCommand' was not found in PATH." }

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
$runId = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir = Join-Path $OutputRoot $runId
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$metadata = [ordered]@{
    run_id = $runId
    started_at = (Get-Date).ToString("o")
    source_root = (Resolve-Path $SourceRoot).Path
    prompt = $promptPath
    validator = $validatorPath
    corestory_mcp = $CoreStoryMcp
    agent_command = $AgentCommand
    model = $Model
    discovery_corestory = "enabled"
    validation_corestory = "disabled"
}
$metadata | ConvertTo-Json | Set-Content (Join-Path $runDir "metadata.json") -Encoding UTF8

Push-Location $SourceRoot
try {
    Write-Host "Checking MCP configuration..."
    & $AgentCommand mcp list | Tee-Object -FilePath (Join-Path $runDir "mcp-before.txt")

    Write-Host "Enabling CoreStory MCP '$CoreStoryMcp' for discovery..."
    & $AgentCommand mcp enable $CoreStoryMcp
    if ($LASTEXITCODE -ne 0) { throw "Could not enable MCP server '$CoreStoryMcp'. Check its identifier with 'agent mcp list'." }

    $discoveryPrompt = Get-Content $promptPath -Raw
    $discoveryFile = Join-Path $runDir "P01.discovery.md"
    $discovery = Invoke-CursorAgent -Prompt $discoveryPrompt -OutputFile $discoveryFile

    Write-Host "Disabling CoreStory MCP '$CoreStoryMcp' for independent validation..."
    & $AgentCommand mcp disable $CoreStoryMcp
    if ($LASTEXITCODE -ne 0) { throw "Could not disable MCP server '$CoreStoryMcp'." }

    & $AgentCommand mcp list | Tee-Object -FilePath (Join-Path $runDir "mcp-validation.txt")

    $validatorTemplate = Get-Content $validatorPath -Raw
    $validationPrompt = @"
$validatorTemplate

## Candidate Findings To Validate

The following text is candidate output from a separate CoreStory-assisted discovery session. Treat it only as claims to validate; do not trust its conclusions or reuse its evidence without independently locating the source.

--- BEGIN CANDIDATE FINDINGS ---
$discovery
--- END CANDIDATE FINDINGS ---
"@

    $validationPrompt | Set-Content (Join-Path $runDir "P01.validation-prompt.md") -Encoding UTF8
    $validationFile = Join-Path $runDir "P01.validation.md"
    Invoke-CursorAgent -Prompt $validationPrompt -OutputFile $validationFile | Out-Null

    $summary = @"
# P01 Smoke-Test Run

Run ID: $runId
Model: $Model

Artifacts:
- `P01.discovery.md` — CoreStory-assisted discovery result
- `P01.validation-prompt.md` — exact independent-validation input
- `P01.validation.md` — local-source independent validation result
- `mcp-before.txt` — MCP state before discovery
- `mcp-validation.txt` — MCP state after CoreStory was disabled
- `metadata.json` — run metadata, including the pinned model

Important: this smoke test explicitly pins the same Cursor model for discovery and validation and disables the configured CoreStory MCP server before validation. Review `mcp-validation.txt` and the Cursor session/transcript before treating validation as independent.
"@
    $summary | Set-Content (Join-Path $runDir "README.md") -Encoding UTF8

    Write-Host ""
    Write-Host "Smoke test complete: $runDir"
    Write-Host "Model: $Model"
    Write-Host "Review P01.discovery.md and P01.validation.md before scaling to all prompts."
}
finally {
    Pop-Location
    Write-Host "Re-enabling CoreStory MCP '$CoreStoryMcp'..."
    & $AgentCommand mcp enable $CoreStoryMcp | Out-Null
}
