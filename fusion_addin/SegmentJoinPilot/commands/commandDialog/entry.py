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
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_createSegmentJoinV044'
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

WORKFLOW_EVENT_ID = f'{CMD_ID}_workflow'
SET_POINT_MODE_NAME = 'Set Point'
_workflow_event = None
_pending_workflow_action = None
_workflow_sketch = None
_waiting_for_sketch_finish = False
_startup_set_point_sketch = None
_position_candidate_entries = []

# Fusion model geometry uses centimeters internally.
PLANE_DISTANCE_TOLERANCE_CM = 1e-6
SJP_NAME_PATTERN = re.compile(r'^SJP_(?:Split|Segment_[AB])_(\d+)$')
POSITION_SKETCH_NAME_PATTERN = re.compile(r'^SJP_PositionSketch_(\d+)$')
POSITION_CANDIDATE_INPUT_PREFIX = 'position_candidate_'
POSITION_MARKER_GRAPHICS_NAME = 'SJP_SelectedPositionMarkers'


# Executed when add-in is run.
def start():
    global _workflow_event

    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    _workflow_event = app.registerCustomEvent(WORKFLOW_EVENT_ID)
    futil.add_handler(_workflow_event, workflow_event_received)
    futil.add_handler(ui.commandTerminated, user_interface_command_terminated)

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
    global _workflow_event

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

    if _workflow_event is not None:
        app.unregisterCustomEvent(WORKFLOW_EVENT_ID)
        _workflow_event = None


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    global _startup_set_point_sketch

    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    args.command.setDialogInitialSize(420, 260)
    inputs = args.command.commandInputs

    mode_input = inputs.addDropDownCommandInput(
        'operation_mode', 'Mode', adsk.core.DropDownStyles.TextListDropDownStyle
    )
    startup_sketch = _startup_set_point_sketch
    _startup_set_point_sketch = None
    start_in_set_point_mode = startup_sketch is not None and startup_sketch.isValid
    mode_input.listItems.add('Create split operation', not start_in_set_point_mode, '')
    mode_input.listItems.add(SET_POINT_MODE_NAME, start_in_set_point_mode, '')

    split_group = inputs.addGroupCommandInput('split_group', 'Split')
    split_group.isVisible = not start_in_set_point_mode
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
        f'Version {__version__} creates separate socket tool bodies for both segments.',
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
    positions_group.isVisible = start_in_set_point_mode
    positions_inputs = positions_group.children
    sketch_input = positions_inputs.addSelectionInput(
        'position_sketch', 'Position sketch', 'Select an SJP sketch or one of its points.'
    )
    sketch_input.addSelectionFilter('Sketches')
    sketch_input.addSelectionFilter('SketchPoints')
    sketch_input.setSelectionLimits(1 if start_in_set_point_mode else 0, 1)
    point_status = positions_inputs.addTextBoxCommandInput(
        'point_status', 'Detected points', 'Select a position sketch.', 2, True
    )
    positions_inputs.addTextBoxCommandInput(
        'selected_position_list',
        'Selected list',
        'No positions selected.',
        4,
        True,
    )
    connector_group = inputs.addGroupCommandInput('connector_group', 'Connector')
    connector_group.isVisible = start_in_set_point_mode
    connector_inputs = connector_group.children
    shape_input = connector_inputs.addDropDownCommandInput(
        'connector_shape', 'Shape', adsk.core.DropDownStyles.TextListDropDownStyle
    )
    shape_input.listItems.add('Round', True, '')
    connector_inputs.addValueInput(
        'connector_diameter',
        'Diameter',
        'mm',
        adsk.core.ValueInput.createByString('6 mm'),
    )
    connector_inputs.addValueInput(
        'connector_length',
        'Total length',
        'mm',
        adsk.core.ValueInput.createByString('12 mm'),
    )

    fit_group = inputs.addGroupCommandInput('fit_group', 'Fit')
    fit_group.isVisible = start_in_set_point_mode
    fit_inputs = fit_group.children
    fit_inputs.addValueInput(
        'radial_clearance',
        'Radial clearance per side',
        'mm',
        adsk.core.ValueInput.createByString('0.20 mm'),
    )
    fit_inputs.addValueInput(
        'depth_clearance',
        'Depth clearance',
        'mm',
        adsk.core.ValueInput.createByString('0.30 mm'),
    )

    if start_in_set_point_mode:
        body_input.setSelectionLimits(0, 1)
        plane_input.setSelectionLimits(0, 1)
        sketch_input.addSelection(startup_sketch)
        _rebuild_position_candidate_inputs(inputs, startup_sketch)

    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_inputs, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_validate_inputs(args: adsk.core.ValidateInputsEventArgs):
    command = adsk.core.Command.cast(args.firingEvent.sender)
    inputs = command.commandInputs if command is not None else args.inputs
    if _is_inspect_mode(inputs):
        _update_position_candidate_status(inputs)
        sketch_input = inputs.itemById('position_sketch')
        diameter_input = inputs.itemById('connector_diameter')
        length_input = inputs.itemById('connector_length')
        clearance_input = inputs.itemById('radial_clearance')
        depth_clearance_input = inputs.itemById('depth_clearance')
        args.areInputsValid = (
            sketch_input is not None
            and sketch_input.selectionCount == 1
            and bool(_selected_position_points(inputs))
            and diameter_input is not None
            and diameter_input.value > 0
            and length_input is not None
            and length_input.value > 0
            and clearance_input is not None
            and clearance_input.value >= 0
            and depth_clearance_input is not None
            and depth_clearance_input.value >= 0
        )
    else:
        args.areInputsValid = _selections_intersect(inputs)


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    if args.input.id == 'operation_mode':
        root_inputs = args.input.parentCommand.commandInputs
        inspect_mode = _is_inspect_mode(root_inputs)
        root_inputs.itemById('split_group').isVisible = not inspect_mode
        root_inputs.itemById('positions_group').isVisible = inspect_mode
        root_inputs.itemById('connector_group').isVisible = inspect_mode
        root_inputs.itemById('fit_group').isVisible = inspect_mode
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
        sketch = (
            _selected_position_sketch(args.input)
            if args.input.selectionCount == 1
            else None
        )
        _rebuild_position_candidate_inputs(args.inputs, sketch)
        return

    if args.input.id.startswith(POSITION_CANDIDATE_INPUT_PREFIX):
        _update_position_candidate_status(args.inputs)
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
        and mode_input.selectedItem.name == SET_POINT_MODE_NAME
    )


def _position_sketch_points(sketch_entity):
    sketch = adsk.fusion.Sketch.cast(sketch_entity)
    if sketch is None:
        return []

    points = []
    origin_token = sketch.originPoint.entityToken
    for index in range(sketch.sketchPoints.count):
        point = sketch.sketchPoints.item(index)
        if point.entityToken == origin_token or point.isReference or not point.isVisible:
            continue
        connected_entities = point.connectedEntities
        if connected_entities is not None and any(
            getattr(entity, 'isReference', False)
            or not getattr(entity, 'isVisible', True)
            for entity in connected_entities
        ):
            continue
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


def _rebuild_position_candidate_inputs(inputs, sketch):
    global _position_candidate_entries

    _position_candidate_entries = []
    positions_group = inputs.itemById('positions_group')
    if positions_group is None:
        return

    candidate_inputs = positions_group.children
    for index in range(candidate_inputs.count - 1, -1, -1):
        candidate_input = candidate_inputs.item(index)
        if candidate_input.id.startswith(POSITION_CANDIDATE_INPUT_PREFIX):
            candidate_input.deleteMe()

    points = _position_sketch_points(sketch)
    for index, point in enumerate(points):
        position = point.geometry
        checkbox = candidate_inputs.addBoolValueInput(
            f'{POSITION_CANDIDATE_INPUT_PREFIX}{index}',
            f'Point {index + 1} ({position.x:.3f}, {position.y:.3f} cm)',
            True,
            '',
            True,
        )
        _position_candidate_entries.append((point, checkbox))
    _update_position_candidate_status(inputs)


def _selected_position_points(inputs):
    sketch = _selected_position_sketch(inputs.itemById('position_sketch'))
    return [
        point
        for point, checkbox in _position_candidate_entries
        if (
            sketch is not None
            and point.isValid
            and checkbox is not None
            and checkbox.isValid
            and checkbox.value
        )
    ]


def _selected_position_entries(inputs):
    sketch = _selected_position_sketch(inputs.itemById('position_sketch'))
    return [
        (index, point)
        for index, (point, checkbox) in enumerate(
            _position_candidate_entries, start=1
        )
        if (
            sketch is not None
            and point.isValid
            and checkbox is not None
            and checkbox.isValid
            and checkbox.value
        )
    ]


def _update_position_candidate_status(inputs):
    status_input = inputs.itemById('point_status')
    if status_input is None:
        return
    sketch = _selected_position_sketch(inputs.itemById('position_sketch'))
    point_count = len(_position_sketch_points(sketch))
    selected_count = len(_selected_position_points(inputs))
    new_status = f'{point_count} position point(s) detected; {selected_count} selected.'
    if status_input.text != new_status:
        status_input.text = new_status
    selected_list_input = inputs.itemById('selected_position_list')
    if selected_list_input is not None:
        selected_entries = _selected_position_entries(inputs)
        selected_text = (
            '\n'.join(
                f'Point {index}: {point.geometry.x:.3f}, '
                f'{point.geometry.y:.3f} cm'
                for index, point in selected_entries
            )
            if selected_entries
            else 'No positions selected.'
        )
        if selected_list_input.text != selected_text:
            selected_list_input.text = selected_text
    _update_position_markers(sketch, _selected_position_points(inputs))


def _delete_position_markers():
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        return

    graphics_groups = design.rootComponent.customGraphicsGroups
    for index in range(graphics_groups.count - 1, -1, -1):
        graphics_group = graphics_groups.item(index)
        if graphics_group.name == POSITION_MARKER_GRAPHICS_NAME:
            graphics_group.deleteMe()


def _update_position_markers(sketch, selected_points):
    _delete_position_markers()
    if sketch is None or not selected_points:
        app.activeViewport.refresh()
        return

    coordinates = []
    marker_half_size_cm = 0.18
    for point in selected_points:
        sketch_position = point.geometry
        marker_endpoints = (
            adsk.core.Point3D.create(
                sketch_position.x - marker_half_size_cm,
                sketch_position.y,
                sketch_position.z,
            ),
            adsk.core.Point3D.create(
                sketch_position.x + marker_half_size_cm,
                sketch_position.y,
                sketch_position.z,
            ),
            adsk.core.Point3D.create(
                sketch_position.x,
                sketch_position.y - marker_half_size_cm,
                sketch_position.z,
            ),
            adsk.core.Point3D.create(
                sketch_position.x,
                sketch_position.y + marker_half_size_cm,
                sketch_position.z,
            ),
        )
        for endpoint in marker_endpoints:
            model_endpoint = sketch.sketchToModelSpace(endpoint)
            if model_endpoint is None:
                continue
            coordinates.extend(
                [model_endpoint.x, model_endpoint.y, model_endpoint.z]
            )

    if not coordinates:
        app.activeViewport.refresh()
        return

    design = adsk.fusion.Design.cast(app.activeProduct)
    marker_group = design.rootComponent.customGraphicsGroups.add()
    marker_group.name = POSITION_MARKER_GRAPHICS_NAME
    marker_coordinates = adsk.fusion.CustomGraphicsCoordinates.create(coordinates)
    marker_lines = marker_group.addLines(marker_coordinates, [], False)
    marker_lines.name = POSITION_MARKER_GRAPHICS_NAME
    marker_lines.weight = 4
    marker_lines.color = adsk.fusion.CustomGraphicsShowThroughColorEffect.create(
        adsk.core.Color.create(255, 40, 20, 255),
        1.0,
    )
    app.activeViewport.refresh()


def _inspect_position_sketch(inputs: adsk.core.CommandInputs):
    sketch_input = inputs.itemById('position_sketch')
    if sketch_input is None or sketch_input.selectionCount != 1:
        ui.messageBox('Select one position sketch.', CMD_NAME)
        return

    sketch = _selected_position_sketch(sketch_input)
    points = _selected_position_points(inputs)
    if not points:
        ui.messageBox('No position points were found.', CMD_NAME)
        return

    point_lines = []
    for index, point in enumerate(points, start=1):
        sketch_position, model_position = _position_coordinates(sketch, point)
        point_lines.append(
            f'Point {index}: '
            f'sketch X={sketch_position.x:.4f} cm, Y={sketch_position.y:.4f} cm; '
            f'model X={model_position.x:.4f} cm, '
            f'Y={model_position.y:.4f} cm, Z={model_position.z:.4f} cm'
        )
    ui.messageBox(
        f'Position sketch: {sketch.name}\n'
        f'Detected position points: {len(points)}\n\n' + '\n'.join(point_lines),
        CMD_NAME,
    )


def _create_round_connector_profile(inputs: adsk.core.CommandInputs):
    sketch_input = inputs.itemById('position_sketch')
    diameter_input = inputs.itemById('connector_diameter')
    length_input = inputs.itemById('connector_length')
    clearance_input = inputs.itemById('radial_clearance')
    depth_clearance_input = inputs.itemById('depth_clearance')
    sketch = _selected_position_sketch(sketch_input)
    selected_entries = _selected_position_entries(inputs)
    selected_numbers = [index for index, _point in selected_entries]
    points = [point for _index, point in selected_entries]
    futil.log(f'Connector profile candidates selected: {selected_numbers}')
    if (
        sketch is None
        or not points
        or diameter_input is None
        or diameter_input.value <= 0
        or length_input is None
        or length_input.value <= 0
        or clearance_input is None
        or clearance_input.value < 0
        or depth_clearance_input is None
        or depth_clearance_input.value < 0
    ):
        ui.messageBox(
            'Select at least one position, enter a positive diameter and length, '
            'and use non-negative radial and depth clearances.',
            CMD_NAME,
        )
        return

    name_match = POSITION_SKETCH_NAME_PATTERN.match(sketch.name)
    if name_match is None:
        ui.messageBox(
            'The selected sketch is not a SegmentJoinPilot position sketch.', CMD_NAME
        )
        return

    operation_suffix = name_match.group(1)
    component = sketch.parentComponent
    profile_names = [
        f'SJP_ConnectorProfile_{operation_suffix}_{index:02d}'
        for index in range(1, len(points) + 1)
    ]
    connector_names = [
        f'SJP_Connector_{operation_suffix}_{index:02d}'
        for index in range(1, len(points) + 1)
    ]
    socket_profile_names = [
        f'SJP_SocketProfile_{operation_suffix}_{index:02d}'
        for index in range(1, len(points) + 1)
    ]
    socket_tool_names = [
        (
            f'SJP_SocketTool_A_{operation_suffix}_{index:02d}',
            f'SJP_SocketTool_B_{operation_suffix}_{index:02d}',
        )
        for index in range(1, len(points) + 1)
    ]
    existing_names = {
        component.sketches.item(index).name
        for index in range(component.sketches.count)
    }
    for profile_name in profile_names:
        if profile_name in existing_names:
            ui.messageBox(
                f'{profile_name} already exists. Delete the existing connector profile '
                'sketches before repeating this test.',
                CMD_NAME,
            )
            return
    for socket_profile_name in socket_profile_names:
        if socket_profile_name in existing_names:
            ui.messageBox(
                f'{socket_profile_name} already exists. Delete the existing socket '
                'profile sketches before repeating this operation.',
                CMD_NAME,
            )
            return
    existing_body_names = {
        component.bRepBodies.item(index).name
        for index in range(component.bRepBodies.count)
    }
    existing_extrude_names = {
        component.features.extrudeFeatures.item(index).name
        for index in range(component.features.extrudeFeatures.count)
    }
    for connector_name in connector_names:
        if connector_name in existing_body_names or connector_name in existing_extrude_names:
            ui.messageBox(
                f'{connector_name} already exists. Delete the existing connector '
                'geometry before repeating this operation.',
                CMD_NAME,
            )
            return
    for tool_names in socket_tool_names:
        for tool_name in tool_names:
            if tool_name in existing_body_names or tool_name in existing_extrude_names:
                ui.messageBox(f'{tool_name} already exists.', CMD_NAME)
                return

    profile_sketches = []
    socket_profile_sketches = []
    connector_extrudes = []
    socket_tool_extrudes = []
    try:
        reference_plane = sketch.referencePlane
        if reference_plane is None:
            raise RuntimeError('The position sketch has no planar reference.')

        radius = diameter_input.value / 2
        extrude_features = component.features.extrudeFeatures
        for point, profile_name, connector_name, socket_profile_name, tool_names in zip(
            points, profile_names, connector_names, socket_profile_names, socket_tool_names
        ):
            profile_sketch = component.sketches.addWithoutEdges(reference_plane)
            if profile_sketch is None:
                raise RuntimeError('Fusion could not create a connector profile sketch.')
            profile_sketches.append(profile_sketch)
            profile_sketch.name = profile_name

            _, model_position = _position_coordinates(sketch, point)
            profile_center = profile_sketch.modelToSketchSpace(model_position)
            if profile_center is None:
                raise RuntimeError('Fusion could not transform a profile center.')

            circle = profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(
                profile_center, radius
            )
            if circle is None:
                raise RuntimeError('Fusion could not create a round connector profile.')
            profile_sketch.isLightBulbOn = True

            if profile_sketch.profiles.count != 1:
                raise RuntimeError(
                    f'{profile_name} did not produce exactly one closed profile.'
                )
            extrude_input = extrude_features.createInput(
                profile_sketch.profiles.item(0),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            )
            if extrude_input is None:
                raise RuntimeError('Fusion could not create the connector extrusion input.')
            if not extrude_input.setSymmetricExtent(
                adsk.core.ValueInput.createByReal(length_input.value), True
            ):
                raise RuntimeError('Fusion could not set the symmetric connector length.')

            connector_extrude = extrude_features.add(extrude_input)
            if connector_extrude is not None:
                connector_extrudes.append(connector_extrude)
            if connector_extrude is None or connector_extrude.bodies.count != 1:
                raise RuntimeError('Fusion could not create one connector body.')
            connector_extrude.name = connector_name
            connector_extrude.bodies.item(0).name = connector_name

            socket_profile_sketch = component.sketches.addWithoutEdges(reference_plane)
            if socket_profile_sketch is None:
                raise RuntimeError('Fusion could not create a socket profile sketch.')
            socket_profile_sketches.append(socket_profile_sketch)
            socket_profile_sketch.name = socket_profile_name

            socket_center = socket_profile_sketch.modelToSketchSpace(model_position)
            if socket_center is None:
                raise RuntimeError('Fusion could not transform a socket profile center.')
            socket_radius = radius + clearance_input.value
            socket_circle = (
                socket_profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(
                    socket_center, socket_radius
                )
            )
            if socket_circle is None:
                raise RuntimeError('Fusion could not create a round socket profile.')
            socket_profile_sketch.isLightBulbOn = True

            socket_depth = length_input.value / 2 + depth_clearance_input.value
            directions = (
                adsk.fusion.ExtentDirections.NegativeExtentDirection,
                adsk.fusion.ExtentDirections.PositiveExtentDirection,
            )
            for tool_name, direction in zip(tool_names, directions):
                socket_extent = adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(socket_depth)
                )
                tool_input = extrude_features.createInput(
                    socket_profile_sketch.profiles.item(0),
                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                )
                if tool_input is None or not tool_input.setOneSideExtent(
                    socket_extent, direction
                ):
                    raise RuntimeError('Fusion could not define a socket tool extrusion.')
                tool_extrude = extrude_features.add(tool_input)
                if tool_extrude is not None:
                    socket_tool_extrudes.append(tool_extrude)
                if tool_extrude is None or tool_extrude.bodies.count != 1:
                    raise RuntimeError('Fusion could not create one socket tool body.')
                tool_extrude.name = tool_name
                tool_extrude.bodies.item(0).name = tool_name

        ui.messageBox(
            f'{len(connector_extrudes)} round connector body/bodies created.\n\n'
            f'Selected candidates: {", ".join(str(number) for number in selected_numbers)}\n'
            f'Connector bodies: {connector_names[0]} through {connector_names[-1]}\n'
            f'Diameter: {diameter_input.expression}\n'
            f'Total length: {length_input.expression}\n'
            f'Radial clearance per side: {clearance_input.expression}\n'
            f'Depth clearance: {depth_clearance_input.expression}',
            CMD_NAME,
        )
    except Exception as error:
        for socket_tool_extrude in reversed(socket_tool_extrudes):
            if socket_tool_extrude.isValid:
                socket_tool_extrude.deleteMe()
        for connector_extrude in reversed(connector_extrudes):
            if connector_extrude.isValid:
                connector_extrude.deleteMe()
        for socket_profile_sketch in reversed(socket_profile_sketches):
            if socket_profile_sketch.isValid:
                socket_profile_sketch.deleteMe()
        for profile_sketch in reversed(profile_sketches):
            if profile_sketch.isValid:
                profile_sketch.deleteMe()
        futil.log(
            f'Round connector profile failed: {error}', adsk.core.LogLevels.ErrorLogLevel
        )
        ui.messageBox(
            f'The round connector profile could not be created.\n\n{error}', CMD_NAME
        )


def _position_coordinates(sketch: adsk.fusion.Sketch, point: adsk.fusion.SketchPoint):
    sketch_position = point.geometry
    model_position = sketch.sketchToModelSpace(sketch_position)
    if model_position is None:
        raise RuntimeError(
            f'Fusion could not transform point {point.entityToken} into model space.'
        )
    return sketch_position, model_position


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
    global _workflow_sketch, _pending_workflow_action

    inputs = args.command.commandInputs
    if _is_inspect_mode(inputs):
        _create_round_connector_profile(inputs)
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

        _workflow_sketch = position_sketch
        _pending_workflow_action = 'activate_sketch'
        ui.statusMessage = (
            f'{CMD_NAME}: split completed. Add position points or sketch geometry to '
            f'{position_sketch.name}, then select Finish Sketch.'
        )
        futil.log(
            f'Split completed: {original_body_name}, {split_feature.name}, '
            f'{position_sketch.name}, {segment_a.name}, {segment_b.name}'
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

    global local_handlers, _position_candidate_entries
    _delete_position_markers()
    _position_candidate_entries = []
    local_handlers = []

    if _pending_workflow_action == 'activate_sketch':
        app.fireCustomEvent(WORKFLOW_EVENT_ID)


def workflow_event_received(args: adsk.core.CustomEventArgs):
    global _pending_workflow_action
    global _waiting_for_sketch_finish
    global _startup_set_point_sketch

    action = _pending_workflow_action
    _pending_workflow_action = None

    if action == 'activate_sketch':
        if _workflow_sketch is None or not _workflow_sketch.isValid:
            ui.messageBox('The newly created position sketch is no longer available.', CMD_NAME)
            return

        sketch_command = ui.commandDefinitions.itemById('SketchActivate')
        if sketch_command is None:
            ui.messageBox('Fusion could not find the Edit Sketch command.', CMD_NAME)
            return

        ui.activeSelections.clear()
        ui.activeSelections.add(_workflow_sketch)
        _waiting_for_sketch_finish = True
        if not sketch_command.execute():
            _waiting_for_sketch_finish = False
            ui.messageBox('Fusion could not open the position sketch for editing.', CMD_NAME)
        return

    if action == 'reopen_set_point':
        if _workflow_sketch is None or not _workflow_sketch.isValid:
            ui.messageBox('The position sketch is no longer available.', CMD_NAME)
            return

        command_definition = ui.commandDefinitions.itemById(CMD_ID)
        if command_definition is None:
            ui.messageBox('SegmentJoinPilot could not be restarted.', CMD_NAME)
            return

        _startup_set_point_sketch = _workflow_sketch
        if not command_definition.execute():
            _startup_set_point_sketch = None
            ui.messageBox('SegmentJoinPilot could not be restarted.', CMD_NAME)


def user_interface_command_terminated(args: adsk.core.ApplicationCommandEventArgs):
    global _pending_workflow_action, _waiting_for_sketch_finish

    if not _waiting_for_sketch_finish or args.commandId != 'SketchStop':
        return

    _waiting_for_sketch_finish = False
    _pending_workflow_action = 'reopen_set_point'
    app.fireCustomEvent(WORKFLOW_EVENT_ID)
