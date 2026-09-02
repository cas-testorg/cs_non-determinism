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
=== winget source status ===
Name    Argument
-----------------------------------------------------
msstore https://storeedgefd.dsx.mp.microsoft.com/v9.0
winget  https://winget.azureedge.net/cache

=== Node.js LTS package lookup ===
  \=== winget version ===
v1.2.10691
=== Search configured winget source for Node.js ===
  \search exit code: -1073741819

=== Exact Node.js LTS lookup against winget source ===
  \show exit code: -1073741819
WindowsProductName    WindowsVersion OsBuildNumber
------------------    -------------- -------------
Windows 10 Enterprise 2009           22631

=== Node.js distribution endpoint ===
HTTP status: 200
Final URI: https://nodejs.org/dist/latest-v22.x/

=== TLS / DNS basics ===

Name       Type IPAddress
----       ---- ---------
nodejs.org    A 104.16.213.131
nodejs.org    A 104.16.212.131
```
