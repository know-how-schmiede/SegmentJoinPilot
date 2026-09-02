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

Test result: Passed in Fusion and confirmed by the project owner.

## Version 0.2.0

### Step 2 - Add branded Fusion command icons

Implemented:

- Updated `version.py` and `SegmentJoinPilot.manifest` to version `0.2.0` as instructed by the project owner.
- Derived the command icons from the existing transparent SegmentJoinPilot icon master.
- Replaced the Autodesk sample command artwork with branded `16x16.png`, `32x32.png`, and `64x64.png` resources.
- Replaced the inherited template command ID and `ACME` namespace with a stable SegmentJoinPilot command ID so Fusion creates a fresh command definition instead of retaining template icon resources.
- A first Fusion retest showed a crossed-tools icon because Fusion preferred the inherited generic `AddInIcon.svg` copies over the branded PNG files.
- Removed those incorrect SVG command resources so Fusion uses the visually verified branded PNG icons.
- A second Fusion retest still showed the generic crossed-tools icon.
- Replaced the manifest icon reference with a branded `AddInIcon.png` so even Fusion's add-in-level fallback uses the correct artwork.
- Assigned a fresh command ID and resource directory for version `0.2.0` to invalidate any persistently cached command resource association.

Scope limitation:

- The menu registration test dialog remains unchanged apart from the displayed version.
- No model selection, geometry, connector, or preview functionality is implemented in this step.

Fusion test:

1. Stop `SegmentJoinPilot` and close Fusion completely to clear the inherited template command definition.
2. Start Fusion again and start `SegmentJoinPilot` in the `Utilities > Add-Ins` dialog.
3. Switch to `Solid > Create`.
4. Verify that the menu entry is named `SegmentJoinPilot 0.2.0`.
5. Verify that the new cyan, navy, and orange SegmentJoinPilot icon is displayed clearly in the menu and toolbar.
6. Select the command and verify that the dialog title is `SegmentJoinPilot 0.2.0`.
7. Stop the add-in and verify that the menu entry disappears.

Test result: Passed in Fusion and confirmed by the project owner after replacing the inherited manifest icon and invalidating the cached command resources.
