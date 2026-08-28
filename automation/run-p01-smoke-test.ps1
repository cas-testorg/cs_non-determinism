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
        [Parameter(Mandatory=$true)][string]$OutputFile,
        [switch]$ApproveMcps,
        [switch]$Force
    )

    Write-Host "Running Cursor agent with model '$Model' -> $OutputFile"

    $args = @(
        "-p", $Prompt,
        "--model", $Model,
        "--mode=ask",
        "--output-format", "text",
        "--trust"
    )

    if ($ApproveMcps) {
        $args += "--approve-mcps"
    }

    if ($Force) {
        $args += "--force"
    }

    $output = & $AgentCommand @args 2>&1
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

$resolvedSourceRoot = (Resolve-Path $SourceRoot).Path

if ([System.IO.Path]::IsPathRooted($OutputRoot)) {
    $outputRootAbsolute = $OutputRoot
}
else {
    $outputRootAbsolute = Join-Path $repoRoot $OutputRoot
}
$outputRootAbsolute = [System.IO.Path]::GetFullPath($outputRootAbsolute)

New-Item -ItemType Directory -Force -Path $outputRootAbsolute | Out-Null
$runId = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir = Join-Path $outputRootAbsolute $runId
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$metadata = [ordered]@{
    run_id = $runId
    started_at = (Get-Date).ToString("o")
    source_root = $resolvedSourceRoot
    prompt = $promptPath
    validator = $validatorPath
    corestory_mcp = $CoreStoryMcp
    agent_command = $AgentCommand
    model = $Model
    output_root = $outputRootAbsolute
    workspace_trust = "explicit --trust"
    discovery_mcp_approval = "explicit --approve-mcps --force"
    discovery_corestory = "enabled"
    validation_corestory = "disabled"
}
$metadata | ConvertTo-Json | Set-Content (Join-Path $runDir "metadata.json") -Encoding UTF8

Push-Location $resolvedSourceRoot
try {
    Write-Host "Checking MCP configuration in source workspace..."
    & $AgentCommand mcp list | Tee-Object -FilePath (Join-Path $runDir "mcp-before.txt")

    Write-Host "Enabling CoreStory MCP '$CoreStoryMcp' for discovery..."
    & $AgentCommand mcp enable $CoreStoryMcp
    if ($LASTEXITCODE -ne 0) { throw "Could not enable MCP server '$CoreStoryMcp'. Check its identifier with 'agent mcp list'." }

    & $AgentCommand mcp list | Tee-Object -FilePath (Join-Path $runDir "mcp-discovery.txt")

    $discoveryPrompt = Get-Content $promptPath -Raw
    $discoveryFile = Join-Path $runDir "P01.discovery.md"
    $discovery = Invoke-CursorAgent -Prompt $discoveryPrompt -OutputFile $discoveryFile -ApproveMcps -Force

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
Workspace trust: explicit --trust
Discovery MCP approval: explicit --approve-mcps --force

Artifacts:
- `P01.discovery.md` — CoreStory-assisted discovery result
- `P01.validation-prompt.md` — exact independent-validation input
- `P01.validation.md` — local-source independent validation result
- `mcp-before.txt` — MCP state before discovery setup
- `mcp-discovery.txt` — MCP state after CoreStory was enabled for discovery
- `mcp-validation.txt` — MCP state after CoreStory was disabled for validation
- `mcp-after.txt` — MCP state after CoreStory was restored
- `metadata.json` — run metadata, including the pinned model, workspace trust, MCP approval/force settings, and absolute output path

Important: discovery explicitly approves MCP use and uses `--force` in the non-interactive Cursor session because `--approve-mcps` alone was observed to reject CoreStory MCP calls. Validation does not pass `--approve-mcps` or `--force` and runs after CoreStory has been disabled. Review the MCP snapshots and Cursor session/transcript before treating the run as controlled evidence.
"@
    $summary | Set-Content (Join-Path $runDir "README.md") -Encoding UTF8

    Write-Host ""
    Write-Host "Smoke test analysis complete: $runDir"
    Write-Host "Model: $Model"
    Write-Host "Restoring CoreStory MCP before exit..."
}
finally {
    # MCP configuration is workspace-scoped, so restoration must occur while
    # the CLI is still running from the source workspace.
    Write-Host "Re-enabling CoreStory MCP '$CoreStoryMcp' in source workspace..."
    & $AgentCommand mcp enable $CoreStoryMcp | Out-Null
    & $AgentCommand mcp list | Tee-Object -FilePath (Join-Path $runDir "mcp-after.txt")
    Pop-Location
}

Write-Host "Smoke test complete: $runDir"
Write-Host "Review P01.discovery.md, P01.validation.md, and the MCP-state snapshots before scaling to all prompts."
