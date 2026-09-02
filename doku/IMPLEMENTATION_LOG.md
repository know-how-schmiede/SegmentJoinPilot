# Implementation Log

## Version 0.1.0

### Step 1 - Register the Fusion menu command

Implemented:

- Added `version.py` with version `0.1.0` as the Python source of truth.
- Synchronized `SegmentJoinPilot.manifest` with version `0.1.0`.
- Disabled the unused Autodesk sample palette commands in the add-in startup list.
- Registered `SegmentJoinPilot 0.1.0` in `Solid > Create`.
- Reduced the command dialog to a read-only menu registration status message.

Scope limitation:

- No model selection, geometry, connector, or preview functionality is implemented in this step.

Fusion test:

1. Open Fusion and switch to the Design workspace.
2. Open the `Utilities > Add-Ins` dialog and start `SegmentJoinPilot`.
3. Switch to the `Solid` tab and open the `Create` panel.
4. Verify that `SegmentJoinPilot 0.1.0` is listed with an icon.
5. Select the command and verify that a dialog titled `SegmentJoinPilot 0.1.0` opens.
6. Verify that the dialog displays the menu registration success message.
7. Close the dialog, stop the add-in, and verify that the menu entry disappears.

Test result: Pending manual test in Fusion.
