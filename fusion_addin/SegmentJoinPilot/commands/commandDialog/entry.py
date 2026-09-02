import adsk.core
import adsk.fusion
import os
import re
from ...lib import fusionAddInUtils as futil
from ... import config
from ...version import __version__
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_createSegmentJoinV020'
CMD_NAME = f'SegmentJoinPilot {__version__}'
CMD_Description = 'Split models into printable segments and add alignment connectors.'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidCreatePanel'
COMMAND_BESIDE_ID = ''

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources_v020', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []

# Fusion model geometry uses centimeters internally.
PLANE_DISTANCE_TOLERANCE_CM = 1e-6
SJP_NAME_PATTERN = re.compile(r'^SJP_(?:Split|Segment_[AB])_(\d+)$')


# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    args.command.setDialogInitialSize(420, 260)
    inputs = args.command.commandInputs

    mode_input = inputs.addDropDownCommandInput(
        'operation_mode', 'Mode', adsk.core.DropDownStyles.TextListDropDownStyle
    )
    mode_input.listItems.add('Create split operation', True, '')
    mode_input.listItems.add('Inspect existing position sketch', False, '')

    split_group = inputs.addGroupCommandInput('split_group', 'Split')
    split_inputs = split_group.children

    body_input = split_inputs.addSelectionInput(
        'solid_body',
        'Solid body',
        'Select one solid body to split.',
    )
    body_input.addSelectionFilter('SolidBodies')
    body_input.setSelectionLimits(1, 1)

    plane_input = split_inputs.addSelectionInput(
        'construction_plane',
        'Construction plane',
        'Select one construction plane as the splitting tool.',
    )
    plane_input.addSelectionFilter('ConstructionPlanes')
    plane_input.setSelectionLimits(1, 1)

    inputs.addTextBoxCommandInput(
        'step_scope',
        '',
        f'Version {__version__} creates a split or inspects standalone sketch points.',
        2,
        True,
    )
    split_inputs.addTextBoxCommandInput(
        'intersection_status',
        'Validation',
        'Select a solid body and a construction plane.',
        2,
        True,
    )

    positions_group = inputs.addGroupCommandInput('positions_group', 'Positions')
    positions_group.isVisible = False
    positions_inputs = positions_group.children
    sketch_input = positions_inputs.addSelectionInput(
        'position_sketch', 'Position sketch', 'Select an SJP sketch or one of its points.'
    )
    sketch_input.addSelectionFilter('Sketches')
    sketch_input.addSelectionFilter('SketchPoints')
    sketch_input.setSelectionLimits(0, 1)
    positions_inputs.addTextBoxCommandInput(
        'point_status', 'Detected points', 'Select a position sketch.', 2, True
    )

    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_inputs, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_validate_inputs(args: adsk.core.ValidateInputsEventArgs):
    command = adsk.core.Command.cast(args.firingEvent.sender)
    inputs = command.commandInputs if command is not None else args.inputs
    if _is_inspect_mode(inputs):
        sketch_input = inputs.itemById('position_sketch')
        args.areInputsValid = (
            sketch_input is not None
            and sketch_input.selectionCount == 1
            and bool(_standalone_sketch_points(_selected_position_sketch(sketch_input)))
        )
    else:
        args.areInputsValid = _selections_intersect(inputs)


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    if args.input.id == 'operation_mode':
        root_inputs = args.input.parentCommand.commandInputs
        inspect_mode = _is_inspect_mode(root_inputs)
        root_inputs.itemById('split_group').isVisible = not inspect_mode
        root_inputs.itemById('positions_group').isVisible = inspect_mode
        root_inputs.itemById('solid_body').setSelectionLimits(
            0 if inspect_mode else 1, 1
        )
        root_inputs.itemById('construction_plane').setSelectionLimits(
            0 if inspect_mode else 1, 1
        )
        root_inputs.itemById('position_sketch').setSelectionLimits(
            1 if inspect_mode else 0, 1
        )
        return

    if args.input.id == 'position_sketch':
        point_status = args.inputs.itemById('point_status')
        point_count = 0
        if args.input.selectionCount == 1:
            point_count = len(_standalone_sketch_points(_selected_position_sketch(args.input)))
        point_status.text = f'{point_count} standalone sketch point(s) detected.'
        return

    if args.input.id not in ('solid_body', 'construction_plane'):
        return

    status_input = args.inputs.itemById('intersection_status')
    body_input = args.inputs.itemById('solid_body')
    plane_input = args.inputs.itemById('construction_plane')

    if body_input.selectionCount != 1 or plane_input.selectionCount != 1:
        status_input.text = 'Select a solid body and a construction plane.'
    elif _selections_intersect(args.inputs):
        status_input.text = 'Valid: the construction plane intersects the solid body.'
    else:
        status_input.text = 'Invalid: the construction plane does not intersect the solid body.'


def _is_inspect_mode(inputs: adsk.core.CommandInputs) -> bool:
    mode_input = inputs.itemById('operation_mode')
    return (
        mode_input is not None
        and mode_input.selectedItem is not None
        and mode_input.selectedItem.name == 'Inspect existing position sketch'
    )


def _standalone_sketch_points(sketch_entity):
    sketch = adsk.fusion.Sketch.cast(sketch_entity)
    if sketch is None:
        return []

    points = []
    origin_token = sketch.originPoint.entityToken
    for index in range(sketch.sketchPoints.count):
        point = sketch.sketchPoints.item(index)
        if point.entityToken == origin_token or point.isReference:
            continue
        connected_entities = point.connectedEntities
        if connected_entities is None or len(connected_entities) == 0:
            points.append(point)
    return points


def _selected_position_sketch(sketch_input):
    if sketch_input is None or sketch_input.selectionCount != 1:
        return None
    entity = sketch_input.selection(0).entity
    sketch = adsk.fusion.Sketch.cast(entity)
    if sketch is not None:
        return sketch
    sketch_point = adsk.fusion.SketchPoint.cast(entity)
    return sketch_point.parentSketch if sketch_point is not None else None


def _inspect_position_sketch(inputs: adsk.core.CommandInputs):
    sketch_input = inputs.itemById('position_sketch')
    if sketch_input is None or sketch_input.selectionCount != 1:
        ui.messageBox('Select one position sketch.', CMD_NAME)
        return

    sketch = _selected_position_sketch(sketch_input)
    points = _standalone_sketch_points(sketch)
    if not points:
        ui.messageBox('No standalone sketch points were found.', CMD_NAME)
        return

    point_lines = []
    for index, point in enumerate(points, start=1):
        position = point.geometry
        point_lines.append(f'Point {index}: X={position.x:.4f} cm, Y={position.y:.4f} cm')
    ui.messageBox(
        f'Position sketch: {sketch.name}\n'
        f'Detected standalone points: {len(points)}\n\n' + '\n'.join(point_lines),
        CMD_NAME,
    )


def _selections_intersect(inputs: adsk.core.CommandInputs) -> bool:
    body_input = inputs.itemById('solid_body')
    plane_input = inputs.itemById('construction_plane')
    if (
        body_input is None
        or body_input.selectionCount != 1
        or plane_input is None
        or plane_input.selectionCount != 1
    ):
        return False

    try:
        body = adsk.fusion.BRepBody.cast(body_input.selection(0).entity)
        construction_plane = adsk.fusion.ConstructionPlane.cast(
            plane_input.selection(0).entity
        )
        if body is None or not body.isSolid or construction_plane is None:
            return False

        temporary_brep_manager = adsk.fusion.TemporaryBRepManager.get()
        intersection = temporary_brep_manager.planeIntersection(
            body,
            construction_plane.geometry,
        )
        return intersection is not None and intersection.edges.count > 0
    except:
        futil.handle_error('plane intersection validation')
        return False


def command_execute(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs
    if _is_inspect_mode(inputs):
        _inspect_position_sketch(inputs)
        return

    if not _selections_intersect(inputs):
        ui.messageBox(
            'The construction plane does not intersect the selected solid body.\n\n'
            'Choose a plane that passes through the body and try again.',
            CMD_NAME,
        )
        return

    body = adsk.fusion.BRepBody.cast(
        inputs.itemById('solid_body').selection(0).entity
    )
    plane = adsk.fusion.ConstructionPlane.cast(
        inputs.itemById('construction_plane').selection(0).entity
    )

    split_feature = None
    position_sketch = None
    timeline_group = None
    try:
        component = body.parentComponent
        original_body_name = body.name
        split_features = component.features.splitBodyFeatures
        split_input = split_features.createInput(body, plane, True)
        if split_input is None:
            raise RuntimeError('Fusion could not create the split-body input.')

        split_feature = split_features.add(split_input)
        if split_feature is None:
            raise RuntimeError('Fusion could not create the split-body feature.')

        result_bodies = [
            split_feature.bodies.item(index)
            for index in range(split_feature.bodies.count)
            if split_feature.bodies.item(index).isSolid
        ]
        if len(result_bodies) != 2:
            result_count = len(result_bodies)
            split_feature.deleteMe()
            split_feature = None
            raise RuntimeError(
                f'The split produced {result_count} solid bodies instead of exactly two.'
            )

        segment_a, segment_b = _classify_split_results(result_bodies, plane.geometry)
        section_faces_a = _find_section_faces(segment_a, plane.geometry)
        section_faces_b = _find_section_faces(segment_b, plane.geometry)
        if not section_faces_a or not section_faces_b:
            raise RuntimeError(
                'Fusion created the split, but the new section faces could not be identified.'
            )

        operation_number = _next_operation_number(component)
        operation_suffix = f'{operation_number:03d}'
        split_feature.name = f'SJP_Split_{operation_suffix}'
        segment_a.name = f'SJP_Segment_A_{operation_suffix}'
        segment_b.name = f'SJP_Segment_B_{operation_suffix}'

        primary_section_face = max(section_faces_a, key=lambda face: face.area)
        position_sketch = component.sketches.add(primary_section_face)
        if position_sketch is None:
            raise RuntimeError('Fusion could not create the position sketch.')
        position_sketch.name = f'SJP_PositionSketch_{operation_suffix}'
        position_sketch.isLightBulbOn = True

        split_timeline_object = split_feature.timelineObject
        sketch_timeline_object = position_sketch.timelineObject
        if split_timeline_object is None or sketch_timeline_object is None:
            raise RuntimeError('Fusion did not create timeline entries for the operation.')

        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            raise RuntimeError('The active product is not a Fusion Design.')
        timeline_group = design.timeline.timelineGroups.add(
            split_timeline_object.index,
            sketch_timeline_object.index,
        )
        if timeline_group is None:
            raise RuntimeError('Fusion could not create the operation timeline group.')
        timeline_group.name = f'SJP_Operation_{operation_suffix}'

        plane_name = getattr(plane, 'name', 'Selected plane')
        ui.messageBox(
            f'Split completed successfully.\n\n'
            f'Original body: {original_body_name}\n'
            f'Construction plane: {plane_name}\n'
            f'Timeline group: {timeline_group.name}\n'
            f'Split feature: {split_feature.name}\n'
            f'Position sketch: {position_sketch.name}\n'
            f'Segment A: {segment_a.name} (negative plane side)\n'
            f'Segment A section faces: {len(section_faces_a)}\n'
            f'Segment B: {segment_b.name} (positive plane side)\n'
            f'Segment B section faces: {len(section_faces_b)}',
            CMD_NAME,
        )
    except Exception as error:
        if timeline_group is not None and timeline_group.isValid:
            timeline_group.deleteMe(False)
        if position_sketch is not None and position_sketch.isValid:
            position_sketch.deleteMe()
        if split_feature is not None and split_feature.isValid:
            split_feature.deleteMe()
        futil.log(f'Split body failed: {error}', adsk.core.LogLevels.ErrorLogLevel)
        ui.messageBox(
            f'The body could not be split.\n\n{error}\n\n'
            'No partial split feature was retained.',
            CMD_NAME,
        )


def _classify_split_results(result_bodies, split_plane: adsk.core.Plane):
    classified_bodies = []
    for body in result_bodies:
        center_of_mass = body.physicalProperties.centerOfMass
        offset = split_plane.origin.vectorTo(center_of_mass)
        signed_distance = split_plane.normal.dotProduct(offset)
        classified_bodies.append((signed_distance, body))

    classified_bodies.sort(key=lambda item: item[0])
    negative_distance, segment_a = classified_bodies[0]
    positive_distance, segment_b = classified_bodies[1]
    if (
        negative_distance >= -PLANE_DISTANCE_TOLERANCE_CM
        or positive_distance <= PLANE_DISTANCE_TOLERANCE_CM
    ):
        raise RuntimeError(
            'The two split results could not be assigned to opposite sides of the plane.'
        )

    return segment_a, segment_b


def _find_section_faces(body: adsk.fusion.BRepBody, split_plane: adsk.core.Plane):
    section_faces = []
    for face_index in range(body.faces.count):
        face = body.faces.item(face_index)
        face_plane = adsk.core.Plane.cast(face.geometry)
        if face_plane is None or not face_plane.normal.isParallelTo(split_plane.normal):
            continue

        plane_offset = split_plane.origin.vectorTo(face_plane.origin)
        distance = abs(split_plane.normal.dotProduct(plane_offset))
        if distance <= PLANE_DISTANCE_TOLERANCE_CM:
            section_faces.append(face)

    return section_faces


def _next_operation_number(component: adsk.fusion.Component) -> int:
    used_numbers = []

    for body_index in range(component.bRepBodies.count):
        match = SJP_NAME_PATTERN.match(component.bRepBodies.item(body_index).name)
        if match:
            used_numbers.append(int(match.group(1)))

    split_features = component.features.splitBodyFeatures
    for feature_index in range(split_features.count):
        match = SJP_NAME_PATTERN.match(split_features.item(feature_index).name)
        if match:
            used_numbers.append(int(match.group(1)))

    return max(used_numbers, default=0) + 1


# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
