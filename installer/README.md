# SegmentJoinPilot Windows installer

The installer copies the add-in to Fusion's per-user add-in directory:

```text
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\SegmentJoinPilot
```

No administrator rights are required.

`UsePreviousAppDir=no` is set intentionally so an update cannot reuse the incorrect legacy installer path. During installation, the obsolete `%APPDATA%\Autodesk\Autodesk Fusion\API\AddIns\SegmentJoinPilot` folder created by the first installer build is removed.

## Build

Install Inno Setup 6, open PowerShell in the repository root, and run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-installer.ps1
```

The build script verifies that the version in `SegmentJoinPilot.iss` matches the add-in manifest. The generated installer is written to `installer\dist` and is intentionally excluded from Git.

Close or stop the add-in in Fusion before installing an update. Restart Fusion after installation so it discovers the installed add-in.
