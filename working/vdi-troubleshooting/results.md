# VDI Troubleshooting Results

Paste command output below the matching test. Redact any credentials, tokens, secrets, or sensitive customer information before committing.

## Test 001 — Environment Discovery

### Output

```text
=== OS ===


=== Package / Runtime Availability ===
winget : FOUND -> C:\Users\carys\AppData\Local\Microsoft\WindowsApps\winget.exe
python : FOUND -> C:\Users\carys\AppData\Local\Microsoft\WindowsApps\python.exe
py : NOT FOUND
git : FOUND -> C:\Users\carys\AppData\Local\Programs\Git\cmd\git.exe
node : NOT FOUND
npm : NOT FOUND
codex : NOT FOUND

=== Versions ===
v1.2.10691Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases.
git version 2.47.1.windows.2
WindowsProductName    WindowsVersion OsBuildNumber
------------------    -------------- -------------
Windows 10 Enterprise 2009           22631
```
