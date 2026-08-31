param(
    [string]$SourceRoot = (Get-Location).Path,
    [string]$CoreStoryMcp = "corestory",
    [string]$AgentCommand = "agent",
    [string]$Model = "gpt-5.4-high",
    [string]$OutputRoot = ".\results\paired-mini",
    [int]$TimeoutMinutes = 90,
    [string[]]$PromptIds = @("P01", "P02", "P04", "P08"),
    [switch]$Resume,
    [switch]$EnableTokenMetrics,
    [string]$TokenLogPath
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$promptMap = [ordered]@{
    P01 = "test-case-2-corestory\prompts\01-uninitialized-indeterminate-state.md"
    P02 = "test-case-2-corestory\prompts\02-shared-state-concurrency.md"
    P04 = "test-case-2-corestory\prompts\04-pointer-dependent-ordering.md"
    P08 = "test-case-2-corestory\prompts\08-schedule-dependent-heuristic-results.md"
}

function Get-TokenLogLineCount {
    if (-not $EnableTokenMetrics) { return 0 }
    if ([string]::IsNullOrWhiteSpace($TokenLogPath)) { throw "-EnableTokenMetrics requires -TokenLogPath." }
    if (-not (Test-Path $TokenLogPath)) { return 0 }
    return @((Get-Content $TokenLogPath)).Count
}

function Export-TokenDelta {
    param(
        [int]$StartLineCount,
        [string]$Destination
    )

    if (-not $EnableTokenMetrics) { return $null }
    if (-not (Test-Path $TokenLogPath)) {
        return [ordered]@{ request_count = 0; note = "Token log was not found after the run." }
    }

    $allLines = @(Get-Content $TokenLogPath)
    $newLines = @()
    if ($allLines.Count -gt $StartLineCount) {
        $newLines = @($allLines | Select-Object -Skip $StartLineCount)
    }
    $newLines | Set-Content -Path $Destination -Encoding UTF8

    $rows = @()
    foreach ($line in $newLines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { $rows += ($line | ConvertFrom-Json) } catch { }
    }

    $totals = [ordered]@{
        request_count = $rows.Count
        input_tokens = [long](($rows | Measure-Object -Property input_tokens -Sum).Sum)
        cached_input_tokens = [long](($rows | Measure-Object -Property cached_input_tokens -Sum).Sum)
        uncached_input_tokens = [long](($rows | Measure-Object -Property uncached_input_tokens -Sum).Sum)
        output_tokens = [long](($rows | Measure-Object -Property output_tokens -Sum).Sum)
        reasoning_tokens = [long](($rows | Measure-Object -Property reasoning_tokens -Sum).Sum)
        visible_output_tokens = [long](($rows | Measure-Object -Property visible_output_tokens -Sum).Sum)
        total_tokens = [long](($rows | Measure-Object -Property total_tokens -Sum).Sum)
        measurement_note = "Rows appended to the configured LiteLLM JSONL log during this serial invocation. Cursor custom-endpoint routing may undercount traffic."
    }
    return $totals
}

function Set-CoreStoryState {
    param([ValidateSet("enabled", "disabled")][string]$State)

    if ($State -eq "enabled") {
        & $AgentCommand mcp enable $CoreStoryMcp | Out-Null
    } else {
        & $AgentCommand mcp disable $CoreStoryMcp | Out-Null
    }
    if ($LASTEXITCODE -ne 0) { throw "Could not set MCP server '$CoreStoryMcp' to $State." }
}

function Invoke-CursorAgentTimed {
    param(
        [Parameter(Mandatory=$true)][string]$Prompt,
        [Parameter(Mandatory=$true)][string]$OutputFile,
        [Parameter(Mandatory=$true)][string]$WorkingDirectory,
        [switch]$ApproveMcps,
        [switch]$Force
    )

    $started = Get-Date
    $tokenStart = Get-TokenLogLineCount
    $argList = @("--model", $Model, "--mode=ask", "--output-format", "text", "--trust")
    if ($ApproveMcps) { $argList += "--approve-mcps" }
    if ($Force) { $argList += "--force" }
    $argList += "-p"
    $argList += $Prompt

    Write-Host "[$($started.ToString('HH:mm:ss'))] Starting Cursor agent -> $OutputFile"

    # Use the same direct native invocation as the proven P01 smoke harness.
    # Start-Job serializes/reshapes argument arrays across the job boundary and
    # caused Cursor print mode to receive '-p' without the prompt text.
    Push-Location $WorkingDirectory
    try {
        $nativeOutput = & $AgentCommand @argList 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    $output = @($nativeOutput)
    $status = if ($exitCode -eq 0) { "completed" } else { "failed" }
    $timedOut = $false

    $output | Set-Content -Path $OutputFile -Encoding UTF8
    $completed = Get-Date
    $elapsed = [math]::Round(($completed - $started).TotalSeconds, 3)

    $tokenMetrics = $null
    if ($EnableTokenMetrics) {
        $tokenMetrics = Export-TokenDelta -StartLineCount $tokenStart -Destination (Join-Path (Split-Path $OutputFile -Parent) "token-usage.jsonl")
        $tokenMetrics | ConvertTo-Json -Depth 5 | Set-Content (Join-Path (Split-Path $OutputFile -Parent) "token-metrics.json") -Encoding UTF8
    }

    Write-Host "[$($completed.ToString('HH:mm:ss'))] $status in $elapsed seconds"

    return [ordered]@{
        started_at = $started.ToString("o")
        completed_at = $completed.ToString("o")
        elapsed_seconds = $elapsed
        exit_code = $exitCode
        status = $status
        timed_out = $timedOut
        timeout_note = "TimeoutMinutes is retained for compatibility but is not enforced while direct invocation is used for reliable prompt transport."
        token_metrics = $tokenMetrics
    }
}

if (-not (Get-Command $AgentCommand -ErrorAction SilentlyContinue)) { throw "Cursor CLI command '$AgentCommand' was not found in PATH." }
$resolvedSourceRoot = (Resolve-Path $SourceRoot).Path

foreach ($id in $PromptIds) {
    if (-not $promptMap.Contains($id)) { throw "Unsupported prompt id '$id'. Supported mini-benchmark prompts: $($promptMap.Keys -join ', ')." }
    $path = Join-Path $repoRoot $promptMap[$id]
    if (-not (Test-Path $path)) { throw "Prompt not found: $path" }
}

if ($EnableTokenMetrics) {
    if ([string]::IsNullOrWhiteSpace($TokenLogPath)) { throw "-EnableTokenMetrics requires -TokenLogPath." }
    $TokenLogPath = [System.IO.Path]::GetFullPath($TokenLogPath)
}

if ([System.IO.Path]::IsPathRooted($OutputRoot)) { $outputRootAbsolute = $OutputRoot }
else { $outputRootAbsolute = Join-Path $repoRoot $OutputRoot }
$outputRootAbsolute = [System.IO.Path]::GetFullPath($outputRootAbsolute)
New-Item -ItemType Directory -Force -Path $outputRootAbsolute | Out-Null

if ($Resume) {
    $existing = Get-ChildItem $outputRootAbsolute -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
    if ($existing) { $runDir = $existing.FullName; $runId = $existing.Name }
}
if (-not $runDir) {
    $runId = Get-Date -Format "yyyyMMdd-HHmmss"
    $runDir = Join-Path $outputRootAbsolute $runId
    New-Item -ItemType Directory -Force -Path $runDir | Out-Null
}

$runMetadata = [ordered]@{
    run_id = $runId
    started_at = (Get-Date).ToString("o")
    source_root = $resolvedSourceRoot
    prompt_ids = $PromptIds
    conditions = @("local", "corestory")
    model = $Model
    corestory_mcp = $CoreStoryMcp
    timeout_minutes = $TimeoutMinutes
    timeout_enforced = $false
    validation_enabled = $false
    token_metrics_enabled = [bool]$EnableTokenMetrics
    token_log_path = if ($EnableTokenMetrics) { $TokenLogPath } else { $null }
    experimental_design = "Identical enhanced prompt and workspace rule; CoreStory MCP availability is the intended condition variable."
}
$runMetadata | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $runDir "metadata.json") -Encoding UTF8

$summaryRows = @()
Push-Location $resolvedSourceRoot
try {
    & $AgentCommand mcp list | Set-Content (Join-Path $runDir "mcp-initial.txt") -Encoding UTF8

    foreach ($promptId in $PromptIds) {
        $promptPath = Join-Path $repoRoot $promptMap[$promptId]
        $prompt = Get-Content $promptPath -Raw
        $promptDir = Join-Path $runDir $promptId
        New-Item -ItemType Directory -Force -Path $promptDir | Out-Null

        foreach ($condition in @("local", "corestory")) {
            $conditionDir = Join-Path $promptDir $condition
            New-Item -ItemType Directory -Force -Path $conditionDir | Out-Null
            $conditionMetadataPath = Join-Path $conditionDir "metadata.json"

            if ($Resume -and (Test-Path $conditionMetadataPath)) {
                try {
                    $prior = Get-Content $conditionMetadataPath -Raw | ConvertFrom-Json
                    if ($prior.status -eq "completed") {
                        Write-Host "Skipping completed $promptId/$condition"
                        $summaryRows += [pscustomobject]@{
                            prompt_id=$promptId; condition=$condition; status=$prior.status; elapsed_seconds=$prior.elapsed_seconds;
                            request_count=$prior.token_metrics.request_count; input_tokens=$prior.token_metrics.input_tokens;
                            output_tokens=$prior.token_metrics.output_tokens; reasoning_tokens=$prior.token_metrics.reasoning_tokens;
                            total_tokens=$prior.token_metrics.total_tokens; output_file=(Join-Path $conditionDir "discovery.md")
                        }
                        continue
                    }
                } catch { }
            }

            try {
                if ($condition -eq "local") {
                    Write-Host "Preparing $promptId/local: CoreStory disabled"
                    Set-CoreStoryState -State disabled
                } else {
                    Write-Host "Preparing $promptId/corestory: CoreStory enabled"
                    Set-CoreStoryState -State enabled
                }
                & $AgentCommand mcp list | Set-Content (Join-Path $conditionDir "mcp-state.txt") -Encoding UTF8

                $outputFile = Join-Path $conditionDir "discovery.md"
                if ($condition -eq "corestory") {
                    $result = Invoke-CursorAgentTimed -Prompt $prompt -OutputFile $outputFile -WorkingDirectory $resolvedSourceRoot -ApproveMcps -Force
                } else {
                    $result = Invoke-CursorAgentTimed -Prompt $prompt -OutputFile $outputFile -WorkingDirectory $resolvedSourceRoot
                }
            } catch {
                $result = [ordered]@{
                    started_at = (Get-Date).ToString("o"); completed_at = (Get-Date).ToString("o"); elapsed_seconds = $null;
                    exit_code = $null; status = "failed"; timed_out = $false; token_metrics = $null; error = $_.Exception.Message
                }
                $_ | Out-String | Set-Content (Join-Path $conditionDir "error.txt") -Encoding UTF8
            }

            $conditionMetadata = [ordered]@{
                prompt_id = $promptId
                condition = $condition
                prompt_path = $promptPath
                model = $Model
                corestory_enabled = ($condition -eq "corestory")
                mcp_approval = if ($condition -eq "corestory") { "--approve-mcps --force" } else { "none; CoreStory disabled" }
                started_at = $result.started_at
                completed_at = $result.completed_at
                elapsed_seconds = $result.elapsed_seconds
                exit_code = $result.exit_code
                status = $result.status
                timed_out = $result.timed_out
                token_metrics = $result.token_metrics
            }
            if ($result.error) { $conditionMetadata.error = $result.error }
            $conditionMetadata | ConvertTo-Json -Depth 8 | Set-Content $conditionMetadataPath -Encoding UTF8

            $tm = $result.token_metrics
            $summaryRows += [pscustomobject]@{
                prompt_id = $promptId
                condition = $condition
                status = $result.status
                elapsed_seconds = $result.elapsed_seconds
                request_count = if ($tm) { $tm.request_count } else { $null }
                input_tokens = if ($tm) { $tm.input_tokens } else { $null }
                output_tokens = if ($tm) { $tm.output_tokens } else { $null }
                reasoning_tokens = if ($tm) { $tm.reasoning_tokens } else { $null }
                total_tokens = if ($tm) { $tm.total_tokens } else { $null }
                output_file = (Join-Path $conditionDir "discovery.md")
            }
            $summaryRows | Export-Csv (Join-Path $runDir "comparison.csv") -NoTypeInformation -Encoding UTF8
        }
    }
}
finally {
    Write-Host "Restoring CoreStory MCP '$CoreStoryMcp' before exit..."
    try {
        Set-CoreStoryState -State enabled
        & $AgentCommand mcp list | Set-Content (Join-Path $runDir "mcp-final.txt") -Encoding UTF8
    } finally {
        Pop-Location
    }
}

$runMetadata.completed_at = (Get-Date).ToString("o")
$runMetadata | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $runDir "metadata.json") -Encoding UTF8
$summaryRows | Export-Csv (Join-Path $runDir "comparison.csv") -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Paired mini-benchmark complete: $runDir"
Write-Host "Review comparison.csv and each condition's discovery.md, metadata.json, and mcp-state.txt."
