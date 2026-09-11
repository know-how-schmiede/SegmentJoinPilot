# SegmentJoinPilot Windows installer

The installer supports both per-user Fusion add-in directories:

```text
%APPDATA%\Autodesk\Autodesk Fusion\API\AddIns\SegmentJoinPilot
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\SegmentJoinPilot
```

It first checks for existing `API\AddIns` directories, then product directories. At each level, `Autodesk Fusion` takes precedence over `Autodesk Fusion 360`. If neither exists, it defaults to `Autodesk Fusion`. The destination page is always shown so users can correct the choice, especially when both directories exist. Directory presence cannot prove which location Fusion uses.

No administrator rights are required. `UsePreviousAppDir=no` ensures each update repeats detection instead of blindly reusing a previous installer path. For unattended installation, use Inno Setup's `/DIR="full destination path"` option when an explicit destination is needed.

Version 0.6.2 no longer deletes the add-in under `Autodesk Fusion`. Only the selected destination is updated; other copies are preserved. See the [installation guide (German)](../doku/INSTALLATION.md) for activation, updates, duplicate copies, manual installation, macOS, and troubleshooting.

## Build

Install Inno Setup 6, open PowerShell in the repository root, and run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-installer.ps1
```

The build script verifies that the version in `SegmentJoinPilot.iss` matches the add-in manifest. The generated installer is written to `installer\dist` and is intentionally excluded from Git.

Close or stop the add-in in Fusion before installing an update. Restart Fusion after installation so it discovers the installed add-in.
