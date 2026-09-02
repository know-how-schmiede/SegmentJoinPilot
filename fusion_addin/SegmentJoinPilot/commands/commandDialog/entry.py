import adsk.core
import adsk.fusion
import os
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
        f'Version {__version__} validates the selections only. No geometry will be changed.',
        2,
        True,
    )
    inputs.addTextBoxCommandInput(
        'intersection_status',
        'Validation',
        'Select a solid body and a construction plane.',
        2,
        True,
    )

    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_inputs, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_validate_inputs(args: adsk.core.ValidateInputsEventArgs):
    inputs = args.inputs
    args.areInputsValid = _selections_intersect(inputs)


def command_input_changed(args: adsk.core.InputChangedEventArgs):
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
    if not _selections_intersect(inputs):
        ui.messageBox(
            'The construction plane does not intersect the selected solid body.\n\n'
            'Choose a plane that passes through the body and try again.',
            CMD_NAME,
        )
        return

    body = inputs.itemById('solid_body').selection(0).entity
    plane = inputs.itemById('construction_plane').selection(0).entity

    body_name = getattr(body, 'name', 'Selected body')
    plane_name = getattr(plane, 'name', 'Selected plane')
    ui.messageBox(
        f'Selection test completed successfully.\n\n'
        f'Solid body: {body_name}\n'
        f'Construction plane: {plane_name}\n\n'
        'No geometry was changed.',
        CMD_NAME,
    )


# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
