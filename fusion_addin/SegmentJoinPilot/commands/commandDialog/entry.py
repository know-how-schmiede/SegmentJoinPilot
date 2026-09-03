import adsk.core
import adsk.fusion
import math
import os
import re
from ...lib import fusionAddInUtils as futil
from ... import config
from ...localization import tr
from ...version import __version__
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_createSegmentJoinV060'
CMD_NAME = f'SegmentJoinPilot {__version__}'
CMD_Description = tr('command_description')

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
DIALOG_BANNER = os.path.join(ICON_FOLDER, 'dialog-banner.png')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []

WORKFLOW_EVENT_ID = f'{CMD_ID}_workflow'
SET_POINT_MODE_NAME = tr('set_point')
SHAPE_LABEL_KEYS = {
    'Round': 'round',
    'D-shaped': 'd_shaped',
    'Oval': 'oval',
    'Rounded rectangle': 'rounded_rectangle',
    'Hexagon': 'hexagon',
}
_workflow_event = None
_pending_workflow_action = None
_workflow_sketch = None
_waiting_for_sketch_finish = False
_startup_set_point_sketch = None
_position_candidate_entries = []
_position_candidate_generation = 0

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

    args.command.setDialogInitialSize(440, 400)
    inputs = args.command.commandInputs

    banner_input = inputs.addImageCommandInput('dialog_banner', '', DIALOG_BANNER)
    banner_input.isFullWidth = True

    mode_input = inputs.addDropDownCommandInput(
        'operation_mode', tr('mode'), adsk.core.DropDownStyles.TextListDropDownStyle
    )
    startup_sketch = _startup_set_point_sketch
    _startup_set_point_sketch = None
    start_in_set_point_mode = startup_sketch is not None and startup_sketch.isValid
    mode_input.listItems.add(tr('create_split'), not start_in_set_point_mode, '')
    mode_input.listItems.add(SET_POINT_MODE_NAME, start_in_set_point_mode, '')

    split_group = inputs.addGroupCommandInput('split_group', tr('split'))
    split_group.isVisible = not start_in_set_point_mode
    split_inputs = split_group.children

    body_input = split_inputs.addSelectionInput(
        'solid_body',
        tr('solid_body'),
        tr('select_body'),
    )
    body_input.addSelectionFilter('SolidBodies')
    body_input.setSelectionLimits(1, 1)

    plane_input = split_inputs.addSelectionInput(
        'construction_plane',
        tr('construction_plane'),
        tr('select_plane'),
    )
    plane_input.addSelectionFilter('ConstructionPlanes')
    plane_input.setSelectionLimits(1, 1)

    inputs.addTextBoxCommandInput(
        'step_scope',
        '',
        tr('scope', version=__version__),
        2,
        True,
    )
    split_inputs.addTextBoxCommandInput(
        'intersection_status',
        tr('validation'),
        tr('select_body_plane'),
        2,
        True,
    )

    positions_group = inputs.addGroupCommandInput('positions_group', tr('positions'))
    positions_group.isVisible = start_in_set_point_mode
    positions_inputs = positions_group.children
    sketch_input = positions_inputs.addSelectionInput(
        'position_sketch', tr('position_sketch'), tr('select_sjp_sketch')
    )
    sketch_input.addSelectionFilter('Sketches')
    sketch_input.addSelectionFilter('SketchPoints')
    sketch_input.setSelectionLimits(1 if start_in_set_point_mode else 0, 1)
    point_status = positions_inputs.addTextBoxCommandInput(
        'point_status', tr('detected_points'), tr('select_position_sketch'), 2, True
    )
    positions_inputs.addTextBoxCommandInput(
        'selected_position_list',
        tr('selected_list'),
        tr('no_positions'),
        4,
        True,
    )
    connector_group = inputs.addGroupCommandInput('connector_group', tr('connector'))
    connector_group.isVisible = start_in_set_point_mode
    connector_inputs = connector_group.children
    shape_input = connector_inputs.addDropDownCommandInput(
        'connector_shape', tr('shape'), adsk.core.DropDownStyles.TextListDropDownStyle
    )
    for index, translation_key in enumerate(SHAPE_LABEL_KEYS.values()):
        shape_input.listItems.add(tr(translation_key), index == 0, '')
    connector_inputs.addValueInput(
        'connector_diameter',
        tr('width_diameter'),
        'mm',
        adsk.core.ValueInput.createByString('6 mm'),
    )
    height_input = connector_inputs.addValueInput(
        'connector_height',
        tr('height'),
        'mm',
        adsk.core.ValueInput.createByString('4 mm'),
    )
    height_input.isVisible = False
    corner_radius_input = connector_inputs.addValueInput(
        'connector_corner_radius',
        tr('corner_radius'),
        'mm',
        adsk.core.ValueInput.createByString('1 mm'),
    )
    corner_radius_input.isVisible = False
    connector_inputs.addValueInput(
        'connector_length',
        tr('total_length'),
        'mm',
        adsk.core.ValueInput.createByString('12 mm'),
    )
    connector_inputs.addValueInput(
        'lead_in_length',
        tr('lead_in'),
        'mm',
        adsk.core.ValueInput.createByString('1 mm'),
    )

    fit_group = inputs.addGroupCommandInput('fit_group', tr('fit'))
    fit_group.isVisible = start_in_set_point_mode
    fit_inputs = fit_group.children
    fit_inputs.addValueInput(
        'radial_clearance',
        tr('radial_clearance'),
        'mm',
        adsk.core.ValueInput.createByString('0.20 mm'),
    )
    fit_inputs.addValueInput(
        'depth_clearance',
        tr('depth_clearance'),
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
        height_input = inputs.itemById('connector_height')
        corner_radius_input = inputs.itemById('connector_corner_radius')
        length_input = inputs.itemById('connector_length')
        lead_in_input = inputs.itemById('lead_in_length')
        clearance_input = inputs.itemById('radial_clearance')
        depth_clearance_input = inputs.itemById('depth_clearance')
        shape = _selected_connector_shape(inputs)
        profile_half_size = (
            min(diameter_input.value, height_input.value) / 2
            if shape in ('Oval', 'Rounded rectangle')
            and diameter_input is not None
            and diameter_input.value > 0
            and height_input is not None
            and height_input.value > 0
            else diameter_input.value / 2
            if shape in ('Round', 'D-shaped', 'Hexagon')
            and diameter_input is not None
            and diameter_input.value > 0
            else 0
        )
        args.areInputsValid = (
            sketch_input is not None
            and sketch_input.selectionCount == 1
            and bool(_selected_position_points(inputs))
            and diameter_input is not None
            and diameter_input.value > 0
            and shape in (
                'Round', 'D-shaped', 'Oval', 'Rounded rectangle', 'Hexagon'
            )
            and (
                shape not in ('Oval', 'Rounded rectangle')
                or (height_input is not None and height_input.value > 0)
            )
            and (
                shape != 'Rounded rectangle'
                or (
                    corner_radius_input is not None
                    and corner_radius_input.value > 0
                    and corner_radius_input.value < profile_half_size
                )
            )
            and length_input is not None
            and length_input.value > 0
            and lead_in_input is not None
            and lead_in_input.value >= 0
            and lead_in_input.value < profile_half_size
            and lead_in_input.value < length_input.value / 2
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

    if args.input.id == 'connector_shape':
        shape = _selected_connector_shape(args.inputs)
        height_input = args.inputs.itemById('connector_height')
        if height_input is not None:
            height_input.isVisible = shape in ('Oval', 'Rounded rectangle')
        corner_radius_input = args.inputs.itemById('connector_corner_radius')
        if corner_radius_input is not None:
            corner_radius_input.isVisible = shape == 'Rounded rectangle'
        return

    if args.input.id == 'position_sketch':
        root_inputs = args.input.parentCommand.commandInputs
        sketch = (
            _selected_position_sketch(args.input)
            if args.input.selectionCount == 1
            else None
        )
        _rebuild_position_candidate_inputs(root_inputs, sketch)
        return

    if args.input.id.startswith(POSITION_CANDIDATE_INPUT_PREFIX):
        _update_position_candidate_status(args.input.parentCommand.commandInputs)
        return

    if args.input.id not in ('solid_body', 'construction_plane'):
        return

    status_input = args.inputs.itemById('intersection_status')
    body_input = args.inputs.itemById('solid_body')
    plane_input = args.inputs.itemById('construction_plane')

    if body_input.selectionCount != 1 or plane_input.selectionCount != 1:
        status_input.text = tr('select_body_plane')
    elif _selections_intersect(args.inputs):
        status_input.text = tr('valid_intersection')
    else:
        status_input.text = tr('invalid_intersection')


def _is_inspect_mode(inputs: adsk.core.CommandInputs) -> bool:
    mode_input = inputs.itemById('operation_mode')
    return (
        mode_input is not None
        and mode_input.selectedItem is not None
        and mode_input.selectedItem.name == SET_POINT_MODE_NAME
    )


def _selected_connector_shape(inputs):
    shape_input = inputs.itemById('connector_shape')
    if shape_input is None or shape_input.selectedItem is None:
        return None
    selected_label = shape_input.selectedItem.name
    return next(
        (shape for shape, key in SHAPE_LABEL_KEYS.items() if selected_label == tr(key)),
        None,
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
    global _position_candidate_entries, _position_candidate_generation

    _position_candidate_entries = []
    _position_candidate_generation += 1
    generation = _position_candidate_generation
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
            f'{POSITION_CANDIDATE_INPUT_PREFIX}{generation}_{index}',
            tr('point', index=index + 1, x=position.x, y=position.y),
            True,
            '',
            True,
        )
        if checkbox is None or not checkbox.isValid:
            raise RuntimeError(
                f'Fusion could not create the selector for position {index + 1}.'
            )
        _position_candidate_entries.append((point, checkbox))
    futil.log(
        f'Position candidate controls rebuilt: generation {generation}, '
        f'{len(_position_candidate_entries)} control(s).'
    )
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
    new_status = tr('point_count', detected=point_count, selected=selected_count)
    if status_input.text != new_status:
        status_input.text = new_status
    selected_list_input = inputs.itemById('selected_position_list')
    if selected_list_input is not None:
        selected_entries = _selected_position_entries(inputs)
        selected_text = (
            '\n'.join(
                tr(
                    'selected_point', index=index,
                    x=point.geometry.x, y=point.geometry.y,
                )
                for index, point in selected_entries
            )
            if selected_entries
            else tr('no_positions')
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
        ui.messageBox(tr('select_one_sketch'), CMD_NAME)
        return

    sketch = _selected_position_sketch(sketch_input)
    points = _selected_position_points(inputs)
    if not points:
        ui.messageBox(tr('no_points_found'), CMD_NAME)
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


def _create_connector_geometry(inputs: adsk.core.CommandInputs):
    sketch_input = inputs.itemById('position_sketch')
    shape_input = inputs.itemById('connector_shape')
    diameter_input = inputs.itemById('connector_diameter')
    height_input = inputs.itemById('connector_height')
    corner_radius_input = inputs.itemById('connector_corner_radius')
    length_input = inputs.itemById('connector_length')
    lead_in_input = inputs.itemById('lead_in_length')
    clearance_input = inputs.itemById('radial_clearance')
    depth_clearance_input = inputs.itemById('depth_clearance')
    sketch = _selected_position_sketch(sketch_input)
    selected_entries = _selected_position_entries(inputs)
    selected_numbers = [index for index, _point in selected_entries]
    points = [point for _index, point in selected_entries]
    shape = _selected_connector_shape(inputs)
    half_width = diameter_input.value / 2 if diameter_input is not None else 0
    half_height = (
        height_input.value / 2
        if shape in ('Oval', 'Rounded rectangle') and height_input is not None
        else half_width
    )
    profile_half_size = min(half_width, half_height)
    futil.log(f'Connector profile candidates selected: {selected_numbers}')
    if (
        sketch is None
        or not points
        or shape not in (
            'Round', 'D-shaped', 'Oval', 'Rounded rectangle', 'Hexagon'
        )
        or diameter_input is None
        or diameter_input.value <= 0
        or (
            shape in ('Oval', 'Rounded rectangle')
            and (height_input is None or height_input.value <= 0)
        )
        or (
            shape == 'Rounded rectangle'
            and (
                corner_radius_input is None
                or corner_radius_input.value <= 0
                or corner_radius_input.value >= profile_half_size
            )
        )
        or length_input is None
        or length_input.value <= 0
        or lead_in_input is None
        or lead_in_input.value < 0
        or lead_in_input.value >= profile_half_size
        or lead_in_input.value >= length_input.value / 2
        or clearance_input is None
        or clearance_input.value < 0
        or depth_clearance_input is None
        or depth_clearance_input.value < 0
    ):
        ui.messageBox(
            tr('invalid_connector'),
            CMD_NAME,
        )
        return

    name_match = POSITION_SKETCH_NAME_PATTERN.match(sketch.name)
    if name_match is None:
        ui.messageBox(
            tr('not_sjp_sketch'), CMD_NAME
        )
        return

    operation_suffix = name_match.group(1)
    component = sketch.parentComponent
    first_connector_index = _next_connector_index(component, operation_suffix)
    connector_indices = list(
        range(first_connector_index, first_connector_index + len(points))
    )
    profile_names = [
        f'SJP_ConnectorProfile_{operation_suffix}_{index:02d}'
        for index in connector_indices
    ]
    connector_names = [
        f'SJP_Connector_{operation_suffix}_{index:02d}'
        for index in connector_indices
    ]
    chamfer_names = [
        f'SJP_ConnectorLeadIn_{operation_suffix}_{index:02d}'
        for index in connector_indices
    ]
    socket_profile_names = [
        f'SJP_SocketProfile_{operation_suffix}_{index:02d}'
        for index in connector_indices
    ]
    socket_tool_names = [
        (
            f'SJP_SocketTool_A_{operation_suffix}_{index:02d}',
            f'SJP_SocketTool_B_{operation_suffix}_{index:02d}',
        )
        for index in connector_indices
    ]
    socket_feature_names = [
        (
            f'SJP_Socket_A_{operation_suffix}_{index:02d}',
            f'SJP_Socket_B_{operation_suffix}_{index:02d}',
        )
        for index in connector_indices
    ]
    existing_names = {
        component.sketches.item(index).name
        for index in range(component.sketches.count)
    }
    for profile_name in profile_names:
        if profile_name in existing_names:
            ui.messageBox(tr('already_exists', name=profile_name), CMD_NAME)
            return
    for socket_profile_name in socket_profile_names:
        if socket_profile_name in existing_names:
            ui.messageBox(tr('already_exists', name=socket_profile_name), CMD_NAME)
            return
    existing_body_names = {
        component.bRepBodies.item(index).name
        for index in range(component.bRepBodies.count)
    }
    existing_extrude_names = {
        component.features.extrudeFeatures.item(index).name
        for index in range(component.features.extrudeFeatures.count)
    }
    existing_combine_names = {
        component.features.combineFeatures.item(index).name
        for index in range(component.features.combineFeatures.count)
    }
    existing_chamfer_names = {
        component.features.chamferFeatures.item(index).name
        for index in range(component.features.chamferFeatures.count)
    }
    for connector_name in connector_names:
        if connector_name in existing_body_names or connector_name in existing_extrude_names:
            ui.messageBox(tr('already_exists', name=connector_name), CMD_NAME)
            return
    if lead_in_input.value > 0:
        for chamfer_name in chamfer_names:
            if chamfer_name in existing_chamfer_names:
                ui.messageBox(tr('already_exists', name=chamfer_name), CMD_NAME)
                return
    for tool_names in socket_tool_names:
        for tool_name in tool_names:
            if tool_name in existing_body_names or tool_name in existing_extrude_names:
                ui.messageBox(tr('already_exists', name=tool_name), CMD_NAME)
                return
    for feature_names in socket_feature_names:
        for feature_name in feature_names:
            if feature_name in existing_combine_names:
                ui.messageBox(tr('already_exists', name=feature_name), CMD_NAME)
                return

    profile_sketches = []
    socket_profile_sketches = []
    connector_extrudes = []
    connector_bodies = []
    connector_chamfers = []
    socket_tool_extrudes = []
    socket_tool_body_pairs = []
    socket_cut_features = []
    extended_timeline_group = None
    created_attributes = []
    try:
        reference_plane = sketch.referencePlane
        if reference_plane is None:
            raise RuntimeError('The position sketch has no planar reference.')

        radius = half_width
        extrude_features = component.features.extrudeFeatures
        chamfer_features = component.features.chamferFeatures
        for point, profile_name, connector_name, chamfer_name, socket_profile_name, tool_names in zip(
            points, profile_names, connector_names, chamfer_names, socket_profile_names, socket_tool_names
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

            _add_connector_profile(
                profile_sketch,
                profile_center,
                radius,
                shape,
                half_height=half_height,
                corner_radius=(
                    corner_radius_input.value
                    if shape == 'Rounded rectangle'
                    else None
                ),
            )
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
            connector_body = connector_extrude.bodies.item(0)
            connector_body.name = connector_name
            connector_bodies.append(connector_body)

            if lead_in_input.value > 0:
                end_edges = _extrude_end_edges(connector_extrude)
                chamfer_input = chamfer_features.createInput2()
                if chamfer_input is None:
                    raise RuntimeError('Fusion could not create the lead-in chamfer input.')
                chamfer_input.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
                    end_edges,
                    adsk.core.ValueInput.createByReal(lead_in_input.value),
                    False,
                )
                connector_chamfer = chamfer_features.add(chamfer_input)
                if connector_chamfer is None:
                    raise RuntimeError(f'Fusion could not create {chamfer_name}.')
                connector_chamfers.append(connector_chamfer)
                connector_chamfer.name = chamfer_name

            socket_profile_sketch = component.sketches.addWithoutEdges(reference_plane)
            if socket_profile_sketch is None:
                raise RuntimeError('Fusion could not create a socket profile sketch.')
            socket_profile_sketches.append(socket_profile_sketch)
            socket_profile_sketch.name = socket_profile_name

            socket_center = socket_profile_sketch.modelToSketchSpace(model_position)
            if socket_center is None:
                raise RuntimeError('Fusion could not transform a socket profile center.')
            socket_radius = radius + clearance_input.value
            _add_connector_profile(
                socket_profile_sketch,
                socket_center,
                socket_radius,
                shape,
                clearance_input.value,
                half_height + clearance_input.value,
                (
                    corner_radius_input.value + clearance_input.value
                    if shape == 'Rounded rectangle'
                    else None
                ),
            )
            socket_profile_sketch.isLightBulbOn = True
            if socket_profile_sketch.profiles.count != 1:
                raise RuntimeError(
                    f'{socket_profile_name} did not produce exactly one closed profile.'
                )

            socket_depth = length_input.value / 2 + depth_clearance_input.value
            directions = (
                adsk.fusion.ExtentDirections.NegativeExtentDirection,
                adsk.fusion.ExtentDirections.PositiveExtentDirection,
            )
            tool_bodies = []
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
                tool_body = tool_extrude.bodies.item(0)
                tool_body.name = tool_name
                tool_bodies.append(tool_body)
            socket_tool_body_pairs.append(tuple(tool_bodies))

        segment_a = _body_by_name(component, f'SJP_Segment_A_{operation_suffix}')
        segment_b = _body_by_name(component, f'SJP_Segment_B_{operation_suffix}')
        if segment_a is None or segment_b is None:
            raise RuntimeError('Fusion could not find both SegmentJoinPilot segment bodies.')

        combine_features = component.features.combineFeatures
        for tool_bodies, feature_names in zip(
            socket_tool_body_pairs, socket_feature_names
        ):
            for target_body, tool_body, feature_name in zip(
                (segment_a, segment_b), tool_bodies, feature_names
            ):
                tools = adsk.core.ObjectCollection.create()
                tools.add(tool_body)
                combine_input = combine_features.createInput(target_body, tools)
                if combine_input is None:
                    raise RuntimeError('Fusion could not create a socket cut input.')
                combine_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
                combine_input.isKeepToolBodies = False
                socket_cut = combine_features.add(combine_input)
                if socket_cut is None:
                    raise RuntimeError(f'Fusion could not create {feature_name}.')
                socket_cut_features.append(socket_cut)
                socket_cut.name = feature_name

        split_feature = _split_feature_by_name(
            component, f'SJP_Split_{operation_suffix}'
        )
        if split_feature is None:
            raise RuntimeError('Fusion could not find the operation split feature.')
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            raise RuntimeError('The active product is not a Fusion Design.')
        extended_timeline_group = _replace_operation_timeline_group(
            design,
            f'SJP_Operation_{operation_suffix}',
            split_feature.timelineObject,
            socket_cut_features[-1].timelineObject,
        )

        common_attributes = {
            'schemaVersion': '1',
            'operationId': operation_suffix,
        }
        _add_sjp_attributes(
            split_feature, created_attributes, **common_attributes, role='split'
        )
        _add_sjp_attributes(
            sketch, created_attributes, **common_attributes, role='positionSketch'
        )
        _add_sjp_attributes(
            segment_a,
            created_attributes,
            **common_attributes,
            role='segment',
            segment='A',
        )
        _add_sjp_attributes(
            segment_b,
            created_attributes,
            **common_attributes,
            role='segment',
            segment='B',
        )
        for connector_index, connector_body in zip(
            connector_indices, connector_bodies
        ):
            _add_sjp_attributes(
                connector_body,
                created_attributes,
                **common_attributes,
                role='connector',
                connectorIndex=str(connector_index),
                shape=shape,
                width=str(diameter_input.value),
                height=(
                    str(height_input.value)
                    if shape in ('Oval', 'Rounded rectangle')
                    else ''
                ),
                cornerRadius=(
                    str(corner_radius_input.value)
                    if shape == 'Rounded rectangle'
                    else ''
                ),
                clearance=str(clearance_input.value),
                leadIn=str(lead_in_input.value),
            )
        for connector_index, connector_chamfer in zip(
            connector_indices, connector_chamfers
        ):
            _add_sjp_attributes(
                connector_chamfer,
                created_attributes,
                **common_attributes,
                role='connectorLeadIn',
                connectorIndex=str(connector_index),
                distance=str(lead_in_input.value),
            )
        for index, socket_cut in enumerate(socket_cut_features):
            _add_sjp_attributes(
                socket_cut,
                created_attributes,
                **common_attributes,
                role='socket',
                connectorIndex=str(connector_indices[index // 2]),
                segment='A' if index % 2 == 0 else 'B',
                shape=shape,
                width=str(diameter_input.value),
                height=(
                    str(height_input.value)
                    if shape in ('Oval', 'Rounded rectangle')
                    else ''
                ),
                cornerRadius=(
                    str(corner_radius_input.value)
                    if shape == 'Rounded rectangle'
                    else ''
                ),
                clearance=str(clearance_input.value),
                depthClearance=str(depth_clearance_input.value),
            )

        height_summary = (
            f'{tr("height")}: {height_input.expression}\n'
            if shape in ('Oval', 'Rounded rectangle')
            else ''
        )
        corner_summary = (
            f'{tr("corner_radius")}: {corner_radius_input.expression}\n'
            if shape == 'Rounded rectangle'
            else ''
        )
        ui.messageBox(
            tr('connector_success', connectors=len(connector_extrudes), sockets=len(socket_cut_features)) + '\n\n'
            f'{tr("selected_candidates")}: {", ".join(str(number) for number in selected_numbers)}\n'
            f'{tr("connector_bodies")}: {connector_names[0]} – {connector_names[-1]}\n'
            f'{tr("shape")}: {tr(SHAPE_LABEL_KEYS[shape])}\n'
            f'{tr("width_diameter")}: {diameter_input.expression}\n'
            f'{height_summary}'
            f'{corner_summary}'
            f'{tr("total_length")}: {length_input.expression}\n'
            f'{tr("lead_in")}: {lead_in_input.expression}\n'
            f'{tr("radial_clearance")}: {clearance_input.expression}\n'
            f'{tr("depth_clearance")}: {depth_clearance_input.expression}',
            CMD_NAME,
        )
    except Exception as error:
        for attribute in reversed(created_attributes):
            if attribute.isValid:
                attribute.deleteMe()
        if extended_timeline_group is not None and extended_timeline_group.isValid:
            extended_timeline_group.deleteMe(False)
        for socket_cut_feature in reversed(socket_cut_features):
            if socket_cut_feature.isValid:
                socket_cut_feature.deleteMe()
        for socket_tool_extrude in reversed(socket_tool_extrudes):
            if socket_tool_extrude.isValid:
                socket_tool_extrude.deleteMe()
        for connector_chamfer in reversed(connector_chamfers):
            if connector_chamfer.isValid:
                connector_chamfer.deleteMe()
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
            f'Connector geometry failed: {error}', adsk.core.LogLevels.ErrorLogLevel
        )
        ui.messageBox(tr('connector_failed', error=error), CMD_NAME)


def _add_connector_profile(
    sketch,
    center,
    radius,
    shape,
    flat_offset=0.0,
    half_height=None,
    corner_radius=None,
):
    if shape == 'Round':
        circle = sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
        if circle is None:
            raise RuntimeError('Fusion could not create a round connector profile.')
        return

    if shape == 'Rounded rectangle':
        _add_rounded_rectangle_profile(
            sketch, center, radius, half_height, corner_radius
        )
        return

    if shape == 'Hexagon':
        _add_hexagon_profile(sketch, center, radius)
        return

    if shape == 'Oval':
        if half_height is None or half_height <= 0:
            raise RuntimeError('The oval profile height is invalid.')
        center_point = adsk.core.Point3D.create(center.x, center.y, center.z)
        if radius >= half_height:
            major_axis_point = adsk.core.Point3D.create(
                center.x + radius, center.y, center.z
            )
            through_point = adsk.core.Point3D.create(
                center.x, center.y + half_height, center.z
            )
        else:
            major_axis_point = adsk.core.Point3D.create(
                center.x, center.y + half_height, center.z
            )
            through_point = adsk.core.Point3D.create(
                center.x + radius, center.y, center.z
            )
        ellipse = sketch.sketchCurves.sketchEllipses.add(
            center_point, major_axis_point, through_point
        )
        if ellipse is None:
            raise RuntimeError('Fusion could not create an oval connector profile.')
        return

    if shape != 'D-shaped':
        raise RuntimeError(f'Unsupported connector shape: {shape}')

    # The base D cuts the source circle at half its radius. For the socket, the
    # arc and flat side are both offset outward by the configured radial clearance.
    chord_x = -radius / 2 if flat_offset == 0 else -(radius - flat_offset) / 2 - flat_offset
    chord_height_squared = radius * radius - chord_x * chord_x
    if chord_height_squared <= 0:
        raise RuntimeError('The D-shaped profile dimensions are invalid.')
    chord_y = math.sqrt(chord_height_squared)
    center_point = adsk.core.Point3D.create(center.x, center.y, center.z)
    start_point = adsk.core.Point3D.create(
        center.x + chord_x, center.y - chord_y, center.z
    )
    start_angle = math.atan2(-chord_y, chord_x)
    sweep_angle = -2 * start_angle
    arc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(
        center_point, start_point, sweep_angle
    )
    if arc is None:
        raise RuntimeError('Fusion could not create the D-shaped profile arc.')
    flat = sketch.sketchCurves.sketchLines.addByTwoPoints(
        arc.endSketchPoint, arc.startSketchPoint
    )
    if flat is None:
        raise RuntimeError('Fusion could not create the D-shaped profile flat side.')


def _add_rounded_rectangle_profile(
    sketch, center, half_width, half_height, corner_radius
):
    if (
        half_height is None
        or corner_radius is None
        or half_width <= 0
        or half_height <= 0
        or corner_radius <= 0
        or corner_radius >= min(half_width, half_height)
    ):
        raise RuntimeError('The rounded-rectangle dimensions are invalid.')

    cx, cy, cz = center.x, center.y, center.z
    arcs = sketch.sketchCurves.sketchArcs
    quarter_turn = math.pi / 2
    arc_specs = (
        ((cx + half_width - corner_radius, cy + half_height - corner_radius),
         (cx + half_width, cy + half_height - corner_radius)),
        ((cx - half_width + corner_radius, cy + half_height - corner_radius),
         (cx - half_width + corner_radius, cy + half_height)),
        ((cx - half_width + corner_radius, cy - half_height + corner_radius),
         (cx - half_width, cy - half_height + corner_radius)),
        ((cx + half_width - corner_radius, cy - half_height + corner_radius),
         (cx + half_width - corner_radius, cy - half_height)),
    )
    rounded_corners = []
    for (center_x, center_y), (start_x, start_y) in arc_specs:
        arc = arcs.addByCenterStartSweep(
            adsk.core.Point3D.create(center_x, center_y, cz),
            adsk.core.Point3D.create(start_x, start_y, cz),
            quarter_turn,
        )
        if arc is None:
            raise RuntimeError('Fusion could not create a rounded corner.')
        rounded_corners.append(arc)

    lines = sketch.sketchCurves.sketchLines
    connections = (
        (rounded_corners[0].endSketchPoint, rounded_corners[1].startSketchPoint),
        (rounded_corners[1].endSketchPoint, rounded_corners[2].startSketchPoint),
        (rounded_corners[2].endSketchPoint, rounded_corners[3].startSketchPoint),
        (rounded_corners[3].endSketchPoint, rounded_corners[0].startSketchPoint),
    )
    for start_point, end_point in connections:
        if lines.addByTwoPoints(start_point, end_point) is None:
            raise RuntimeError('Fusion could not close the rounded-rectangle profile.')


def _add_hexagon_profile(sketch, center, apothem):
    if apothem <= 0:
        raise RuntimeError('The hexagon dimensions are invalid.')

    circumradius = apothem / math.cos(math.pi / 6)
    vertices = [
        adsk.core.Point3D.create(
            center.x + circumradius * math.cos(index * math.pi / 3),
            center.y + circumradius * math.sin(index * math.pi / 3),
            center.z,
        )
        for index in range(6)
    ]
    lines = sketch.sketchCurves.sketchLines
    first_line = lines.addByTwoPoints(vertices[0], vertices[1])
    if first_line is None:
        raise RuntimeError('Fusion could not create the hexagon profile.')

    first_point = first_line.startSketchPoint
    previous_point = first_line.endSketchPoint
    for vertex in vertices[2:]:
        line = lines.addByTwoPoints(previous_point, vertex)
        if line is None:
            raise RuntimeError('Fusion could not create the hexagon profile.')
        previous_point = line.endSketchPoint
    if lines.addByTwoPoints(previous_point, first_point) is None:
        raise RuntimeError('Fusion could not close the hexagon profile.')


def _extrude_end_edges(extrude_feature):
    edges = adsk.core.ObjectCollection.create()
    for faces in (extrude_feature.startFaces, extrude_feature.endFaces):
        if faces is None or faces.count != 1:
            raise RuntimeError('Fusion could not identify one face at each connector end.')
        face = faces.item(0)
        for edge_index in range(face.edges.count):
            edges.add(face.edges.item(edge_index))
    if edges.count < 2:
        raise RuntimeError('Fusion could not identify the connector end edges.')
    return edges


def _position_coordinates(sketch: adsk.fusion.Sketch, point: adsk.fusion.SketchPoint):
    sketch_position = point.geometry
    model_position = sketch.sketchToModelSpace(sketch_position)
    if model_position is None:
        raise RuntimeError(
            f'Fusion could not transform point {point.entityToken} into model space.'
        )
    return sketch_position, model_position


def _body_by_name(component: adsk.fusion.Component, name: str):
    for index in range(component.bRepBodies.count):
        body = component.bRepBodies.item(index)
        if body.name == name:
            return body
    return None


def _next_connector_index(component, operation_suffix):
    name_pattern = re.compile(
        rf'^SJP_(?:ConnectorProfile|Connector|ConnectorLeadIn|SocketProfile|'
        rf'SocketTool_[AB]|Socket_[AB])_{re.escape(operation_suffix)}_(\d+)$'
    )
    names = []
    collections = (
        component.sketches,
        component.bRepBodies,
        component.features.extrudeFeatures,
        component.features.chamferFeatures,
        component.features.combineFeatures,
    )
    for collection in collections:
        for index in range(collection.count):
            names.append(collection.item(index).name)

    used_indices = []
    for name in names:
        match = name_pattern.match(name)
        if match is not None:
            used_indices.append(int(match.group(1)))
    return max(used_indices, default=0) + 1


def _split_feature_by_name(component: adsk.fusion.Component, name: str):
    split_features = component.features.splitBodyFeatures
    for index in range(split_features.count):
        split_feature = split_features.item(index)
        if split_feature.name == name:
            return split_feature
    return None


def _replace_operation_timeline_group(design, group_name, start_object, end_object):
    timeline_groups = design.timeline.timelineGroups
    existing_group = None
    for index in range(timeline_groups.count):
        candidate = timeline_groups.item(index)
        if candidate.name == group_name:
            existing_group = candidate
            break

    if existing_group is None:
        raise RuntimeError(f'Fusion could not find timeline group {group_name}.')

    old_start_object = existing_group.item(0)
    old_end_object = existing_group.item(existing_group.count - 1)
    if not existing_group.deleteMe(False):
        raise RuntimeError(f'Fusion could not expand and replace {group_name}.')

    old_start_index = old_start_object.index
    old_end_index = old_end_object.index
    start_index = start_object.index
    end_index = end_object.index
    if start_index < 0 or end_index < start_index:
        restored_group = timeline_groups.add(old_start_index, old_end_index)
        if restored_group is not None:
            restored_group.name = group_name
        raise RuntimeError('Fusion returned invalid timeline indices for the operation.')

    replacement = timeline_groups.add(start_index, end_index)
    if replacement is None:
        restored_group = timeline_groups.add(old_start_index, old_end_index)
        if restored_group is not None:
            restored_group.name = group_name
        raise RuntimeError(f'Fusion could not recreate timeline group {group_name}.')
    replacement.name = group_name
    return replacement


def _add_sjp_attributes(entity, created_attributes, **values):
    for name, value in values.items():
        existing_attribute = entity.attributes.itemByName(
            'SegmentJoinPilot', name
        )
        if existing_attribute is not None:
            existing_attribute.value = str(value)
            continue
        attribute = entity.attributes.add('SegmentJoinPilot', name, str(value))
        if attribute is None:
            raise RuntimeError(
                f'Fusion could not store SegmentJoinPilot attribute {name}.'
            )
        created_attributes.append(attribute)


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
        _create_connector_geometry(inputs)
        return

    if not _selections_intersect(inputs):
        ui.messageBox(tr('split_no_intersection'), CMD_NAME)
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
        ui.statusMessage = tr(
            'split_complete', name=CMD_NAME, sketch=position_sketch.name
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
        ui.messageBox(tr('split_failed', error=error), CMD_NAME)


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
            ui.messageBox(tr('new_sketch_unavailable'), CMD_NAME)
            return

        sketch_command = ui.commandDefinitions.itemById('SketchActivate')
        if sketch_command is None:
            ui.messageBox(tr('edit_command_missing'), CMD_NAME)
            return

        ui.activeSelections.clear()
        ui.activeSelections.add(_workflow_sketch)
        _waiting_for_sketch_finish = True
        if not sketch_command.execute():
            _waiting_for_sketch_finish = False
            ui.messageBox(tr('open_sketch_failed'), CMD_NAME)
        return

    if action == 'reopen_set_point':
        if _workflow_sketch is None or not _workflow_sketch.isValid:
            ui.messageBox(tr('sketch_unavailable'), CMD_NAME)
            return

        command_definition = ui.commandDefinitions.itemById(CMD_ID)
        if command_definition is None:
            ui.messageBox(tr('restart_failed'), CMD_NAME)
            return

        _startup_set_point_sketch = _workflow_sketch
        if not command_definition.execute():
            _startup_set_point_sketch = None
            ui.messageBox(tr('restart_failed'), CMD_NAME)


def user_interface_command_terminated(args: adsk.core.ApplicationCommandEventArgs):
    global _pending_workflow_action, _waiting_for_sketch_finish

    if not _waiting_for_sketch_finish or args.commandId != 'SketchStop':
        return

    _waiting_for_sketch_finish = False
    _pending_workflow_action = 'reopen_set_point'
    app.fireCustomEvent(WORKFLOW_EVENT_ID)
