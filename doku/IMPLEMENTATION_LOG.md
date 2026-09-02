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

## Version 0.3.0

### Step 3 - Select a solid body and construction plane

Implemented:

- Updated `version.py` and `SegmentJoinPilot.manifest` to version `0.3.0` as instructed by the project owner.
- Replaced the menu registration status content with an English `Split` input group.
- Added a required single-selection input filtered to solid BRep bodies.
- Added a required single-selection input filtered to construction planes.
- Added validation that enables confirmation only when both selections contain exactly one entity.
- Added a completion message that reports both selected entity names and explicitly confirms that no geometry was changed.

Scope limitation:

- The selected body is not split in this step.
- No intersection test, sketch selection, connector, socket, or preview functionality is implemented.

Fusion test:

1. Stop and restart `SegmentJoinPilot` in the `Utilities > Add-Ins` dialog.
2. Open or create a Design document containing one solid body and one construction plane.
3. Run `SegmentJoinPilot 0.3.0` from `Solid > Create`.
4. Verify that the dialog title and menu entry show version `0.3.0`.
5. Verify that `Solid body` accepts a solid body but does not accept a face, sketch, or mesh body.
6. Verify that `Construction plane` accepts a construction plane but does not accept a planar face.
7. Verify that the OK button is disabled until both required selections are present.
8. Confirm the dialog and verify that the completion message contains both selected names.
9. Verify that no geometry or timeline entry was created or changed.
10. Cancel a second invocation and verify that the model remains unchanged.

Test result: Passed by project-owner approval to continue with the next step.

## Version 0.3.1

### Step 4 - Validate the body-plane intersection

Implemented:

- Updated `version.py` and `SegmentJoinPilot.manifest` to version `0.3.1` as instructed by the project owner.
- Added a non-destructive intersection check using Fusion's `TemporaryBRepManager.planeIntersection` API.
- Added an English validation status that updates when the body or construction-plane selection changes.
- Disabled confirmation when the selected construction plane does not produce intersection curves with the solid body.
- Added a defensive execute-time intersection check and a clear English error message.

Scope limitation:

- The intersection test checks for section curves; the actual split and verification of exactly two result solids are not implemented yet.
- No document geometry or timeline item is created or changed.

Fusion test:

1. Stop and restart `SegmentJoinPilot` in the `Utilities > Add-Ins` dialog.
2. Open a Design document containing a solid body.
3. Create one construction plane that passes through the body and another plane outside it.
4. Run `SegmentJoinPilot 0.3.1` from `Solid > Create`.
5. Select the body and the outside plane; verify that the validation reads `Invalid` and OK remains disabled.
6. Replace the plane selection with the intersecting plane; verify that the validation reads `Valid` and OK becomes enabled.
7. Confirm the dialog and verify that the success message shows both selected names.
8. Verify that the body, feature count, and timeline remain unchanged.
9. Repeat with a curved solid such as a cylinder or sphere and verify both a passing and a non-passing plane.

Test result: Passed in Fusion and confirmed by the project owner.

## Version 0.3.2

### Step 5 - Split the selected body into two solids

Implemented:

- Updated `version.py` and `SegmentJoinPilot.manifest` to version `0.3.2` as instructed by the project owner.
- Created a native Fusion `SplitBodyFeature` from the selected solid body and construction plane.
- Enabled splitting-tool extension for the infinite construction-plane split.
- Read the result bodies from the created feature rather than relying on component body-list positions.
- Required exactly two solid result bodies for a successful operation.
- Added rollback of the newly created split feature if creation or result validation fails.
- Added clear English success and error messages.

Scope limitation:

- Result bodies and the split feature retain Fusion's default names in this step.
- No section-face detection, timeline grouping, connector, socket, or preview functionality is implemented.

Fusion test:

1. Stop and restart `SegmentJoinPilot` in the `Utilities > Add-Ins` dialog.
2. Create a new Design document with one simple solid box and a construction plane passing through its center.
3. Run `SegmentJoinPilot 0.3.2` from `Solid > Create` and select the box and plane.
4. Confirm the dialog and verify that the success message reports exactly two solid bodies.
5. Verify in the Browser that the original body was split into two solid bodies.
6. Verify that exactly one Split Body feature was added to the timeline.
7. Undo once and verify that the original single body is restored.
8. Repeat with an angled plane that passes through the box.
9. Verify that an outside plane is still rejected before execution.

Test result: Passed in Fusion and confirmed by the project owner.

## Version 0.3.3

### Step 6 - Identify segment sides and section faces

Implemented:

- Updated `version.py` and `SegmentJoinPilot.manifest` to version `0.3.3` as instructed by the project owner.
- Classified the two split results by signed center-of-mass distance from the selected construction plane.
- Defined Segment A as the result on the negative side of the plane normal and Segment B as the result on the positive side.
- Identified section faces geometrically by planar surface type, parallel normals, and coplanar distance tolerance.
- Supported more than one coplanar section face per segment instead of assuming a single face.
- Added rollback when the results cannot be assigned to opposite plane sides or section faces cannot be found on both segments.
- Reported the temporary Fusion body names, side assignment, and section-face counts in the completion message.

Scope limitation:

- Segment bodies and the split feature are not renamed yet.
- Detected section-face references are not persisted yet.
- No timeline group, connector, socket, or preview functionality is implemented.

Fusion test:

1. Stop and restart `SegmentJoinPilot` in the `Utilities > Add-Ins` dialog.
2. Create a simple box and a construction plane through its center.
3. Run `SegmentJoinPilot 0.3.3`, select both entities, and confirm.
4. Verify that the completion message identifies Segment A on the negative plane side and Segment B on the positive plane side.
5. Verify that at least one section face is reported for both segments.
6. Reverse or recreate the construction plane with the opposite normal direction and verify that the A/B assignment swaps accordingly.
7. Repeat with an angled plane and verify that both segments and their section faces are still identified.
8. Verify that the operation creates only the split feature and two result bodies, with no additional geometry.

Test result: Pending manual test in Fusion.
