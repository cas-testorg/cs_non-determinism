# VDI Troubleshooting Scratchpad

Internal working area for troubleshooting token-metering and custom-model routing from the Windows 11 VDI.

## Purpose

Use GitHub as a low-friction bridge between ChatGPT and the customer VDI:

1. Read the next command from `commands.md` in the VDI browser.
2. Copy the command into PowerShell.
3. Paste the resulting text output into `results.md`.
4. Review the output and update `commands.md` with the next test.

## Scope

Current focus:

- Verify the Windows 11 VDI toolchain.
- Install or validate a reference coding-agent client if practical.
- Prove the LiteLLM proxy path independently of Cursor.
- Isolate whether failures are caused by Cursor custom-model routing, LiteLLM, or the upstream Azure OpenAI deployment.

## Rules

- Do **not** commit Azure keys, bearer tokens, passwords, customer secrets, or other credentials.
- Redact sensitive values before pasting output.
- Prefer text output over screenshots.
- Run one small test at a time so results remain attributable.
- This directory is temporary/internal working material and is not customer-facing documentation.

## Current Environment

- Client: Windows 11 VDI
- Shell: PowerShell
- Node.js: not currently installed
- LiteLLM: existing token-metering proxy work in progress
- Cursor: available in the client environment
- Upstream model: Azure OpenAI custom GPT-5.4 deployment
