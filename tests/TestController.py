from unittest.mock import MagicMock

from UM.Controller import Controller
from UM.Event import ViewEvent, Event
from UM.InputDevice import InputDevice
from UM.Mesh.MeshData import MeshData
from UM.Scene.SceneNode import SceneNode
from UM.Stage import Stage
from UM.Tool import Tool
from UM.View.View import View


def test_addView(application):
    controller = Controller(application)
    view_1 = View()
    view_1.setPluginId("test_1")
    view_2 = View()
    view_2.setPluginId("test_1")
    controller.viewsChanged.emit = MagicMock()
    controller.addView(view_1)

    assert controller.getAllViews() == {"test_1": view_1}
    assert controller.viewsChanged.emit.call_count == 1

    # Attempting to add the same view twice should not have any effect.
    controller.addView(view_1)
    assert controller.getAllViews() == {"test_1": view_1}
    assert controller.viewsChanged.emit.call_count == 1

    # It has the same ID (although the view is different). In that case it still shouldn't be added.
    controller.addView(view_2)
    assert controller.getAllViews() == {"test_1": view_1}
    assert controller.viewsChanged.emit.call_count == 1


def test_getView(application):
    controller = Controller(application)
    view_1 = View()
    view_1.setPluginId("test_1")
    view_2 = View()
    view_2.setPluginId("test_2")

    controller.addView(view_1)
    controller.addView(view_2)

    assert controller.getView("test_1") == view_1
    assert controller.getView("test_2") == view_2
    assert controller.getView("NOPE") is None


def test_setActiveView(application):
    controller = Controller(application)
    view_1 = View()
    view_1.setPluginId("test_1")
    view_2 = View()
    view_2.setPluginId("test_2")

    controller.addView(view_1)
    controller.addView(view_2)
    controller.activeViewChanged.emit = MagicMock()

    # Attempting to set the view to a non existing one shouldn't do anything
    controller.setActiveView("blorp")
    assert controller.activeViewChanged.emit.call_count == 0

    view_1.event = MagicMock()
    controller.setActiveView("test_1")
    assert controller.activeViewChanged.emit.call_count == 1
    assert controller.getActiveView() == view_1
    # Ensure that the view gets notified that it was activated.
    assert view_1.event.call_args_list[0][0][0].type == Event.ViewActivateEvent

    controller.setActiveView("test_2")
    assert controller.getActiveView() == view_2
    assert controller.activeViewChanged.emit.call_count == 2
    # Ensure that the view was notified that it got deactivated again
    assert view_1.event.call_args_list[1][0][0].type == Event.ViewDeactivateEvent


def test_addRemoveInputDevice(application):
    controller = Controller(application)

    input_device = InputDevice()
    input_device.setPluginId("input_device")

    controller.addInputDevice(input_device)
    controller.addInputDevice(input_device) # Doing it twice shouldn't cause issues.

    assert controller.getInputDevice("input_device") == input_device
    assert controller.getInputDevice("OMGZOMG") is None  # This device isn't added

    controller.removeInputDevice("input_device")
    assert controller.getInputDevice("input_device") is None

    controller.removeInputDevice("input_device") #Removing it again shouldn't cause issues.


def test_setCameraTool(application):
    controller = Controller(application)

    camera_tool = Tool()
    camera_tool.setPluginId("camera_tool")

    controller.addTool(camera_tool)

    controller.setCameraTool(camera_tool)
    assert controller.getCameraTool() == camera_tool

    controller.setCameraTool("")
    assert controller.getCameraTool() is None

    controller.setCameraTool("camera_tool")
    assert controller.getCameraTool() == camera_tool


def test_getSetToolsEnabled(application):
    controller = Controller(application)

    controller.setToolsEnabled(True)
    assert controller.getToolsEnabled()

    controller.setToolsEnabled(False)
    assert not controller.getToolsEnabled()

def test_addStage(application):
    controller = Controller(application)
    stage_1 = Stage()
    stage_1.setPluginId("test_1")

    stage_2 = Stage()
    stage_2.setPluginId("test_1")
    controller.stagesChanged.emit = MagicMock()

    controller.addStage(stage_1)
    assert controller.stagesChanged.emit.call_count == 1
    assert controller.getAllStages() == {"test_1": stage_1}

    # Adding it again shouldn't influence anything
    controller.addStage(stage_1)
    assert controller.stagesChanged.emit.call_count == 1
    assert controller.getAllStages() == {"test_1": stage_1}

    # Adding a different stage (but with the same ID) should also not do anything!
    controller.addStage(stage_2)
    assert controller.stagesChanged.emit.call_count == 1
    assert controller.getAllStages() == {"test_1": stage_1}


def test_setActiveStage(application):
    controller = Controller(application)
    controller.activeStageChanged.emit = MagicMock()

    stage_1 = Stage()
    stage_1.setPluginId("test_1")
    stage_1.onStageSelected = MagicMock()
    stage_1.onStageDeselected = MagicMock()

    stage_2 = Stage()
    stage_2.setPluginId("test_2")
    controller.addStage(stage_1)
    controller.addStage(stage_2)

    # Attempting to set the stage to a non existing one shouldn't do anything
    controller.setActiveStage("blorp")
    assert controller.activeStageChanged.emit.call_count == 0

    # Changing it from no state to an added state should work.
    controller.setActiveStage("test_1")
    assert controller.getActiveStage() == stage_1
    stage_1.onStageSelected.assert_called_once_with()

    # Attempting to change to a stage that doesn't exist shouldn't do anything.
    controller.setActiveStage("blorp")
    assert controller.getActiveStage() == stage_1
    stage_1.onStageSelected.assert_called_once_with()
    stage_1.onStageDeselected.assert_not_called()

    # Changing to the already active stage should also not do anything.
    controller.setActiveStage("test_1")
    assert controller.getActiveStage() == stage_1
    stage_1.onStageSelected.assert_called_once_with()
    stage_1.onStageDeselected.assert_not_called()


    # Actually changing it to a stage that is added and not active should have an effect
    controller.setActiveStage("test_2")
    stage_1.onStageDeselected.assert_called_with()
    assert controller.getActiveStage() == stage_2


def test_getStage(application):
    controller = Controller(application)
    stage_1 = Stage()
    stage_1.setPluginId("test_1")
    stage_2 = Stage()
    stage_2.setPluginId("test_2")

    controller.addStage(stage_1)
    controller.addStage(stage_2)

    assert controller.getStage("test_1") == stage_1
    assert controller.getStage("test_2") == stage_2
    assert controller.getStage("NOPE") is None


def test_toolOperations(application):
    controller = Controller(application)
    controller.toolOperationStarted.emit = MagicMock()
    controller.toolOperationStopped.emit = MagicMock()
    test_tool_1 = Tool()
    test_tool_1.setPluginId("test_tool_1")

    controller.addTool(test_tool_1)
    # The tool starts an operation
    test_tool_1.operationStarted.emit(test_tool_1)

    controller.toolOperationStarted.emit.assert_called_with(test_tool_1)
    assert controller.isToolOperationActive()

    # The tool stops doing something
    test_tool_1.operationStopped.emit(test_tool_1)
    controller.toolOperationStopped.emit.assert_called_with(test_tool_1)
    assert not controller.isToolOperationActive()


def test_addTools(application):
    controller = Controller(application)

    # Switch out the emits with a mock.
    controller.toolsChanged.emit = MagicMock()
    controller.activeToolChanged.emit = MagicMock()

    test_tool_1 = Tool()
    test_tool_1.setPluginId("test_tool_1")
    test_tool_1.event = MagicMock()
    test_tool_2 = Tool()
    test_tool_2.setPluginId("test_tool_2")

    controller.addTool(test_tool_1)
    assert controller.toolsChanged.emit.call_count == 1

    controller.addTool(test_tool_2)
    assert controller.toolsChanged.emit.call_count == 2

    controller.addTool(test_tool_1)
    assert controller.toolsChanged.emit.call_count == 2
    assert len(controller.getAllTools()) == 2

    # Set active tool with an unknown name.
    controller.setActiveTool("nope nope!")
    assert controller.getActiveTool() is None
    assert controller.activeToolChanged.emit.call_count == 0

    # Set active tool by reference
    controller.setActiveTool(test_tool_1)
    assert controller.getActiveTool() == test_tool_1
    assert controller.activeToolChanged.emit.call_count == 1
    # Check if the tool got notified that it's not active.
    assert test_tool_1.event.call_args_list[0][0][0].type == Event.ToolActivateEvent

    # Set active tool by ID, but the same as is already active.
    controller.setActiveTool("test_tool_1")
    assert controller.getActiveTool() == test_tool_1
    assert controller.activeToolChanged.emit.call_count == 1

    # Set active tool by ID
    controller.setActiveTool("test_tool_2")
    assert controller.getActiveTool() == test_tool_2
    assert controller.activeToolChanged.emit.call_count == 2
    # Check if the tool got notified that it's no longer active.
    assert test_tool_1.event.call_args_list[1][0][0].type == Event.ToolDeactivateEvent

    assert controller.getTool("ZOMG") is None
    assert controller.getTool("test_tool_1") == test_tool_1
    assert controller.getTool("test_tool_2") == test_tool_2


def test_eventHandling(application):
    controller = Controller(application)

    selection_tool = Tool()
    selection_tool.setPluginId("selection_tool")
    selection_tool.event = MagicMock(return_value = True)

    camera_tool = Tool()
    camera_tool.setPluginId("camera_tool")
    camera_tool.event = MagicMock(return_value=True)

    random_tool = Tool()
    random_tool.setPluginId("random_tool")
    random_tool.event = MagicMock(return_value=True)

    event = Event(1)


    controller.setCameraTool(camera_tool)
    controller.event(event)
    # Only the camera tool should be called now.
    camera_tool.event.assert_called_once_with(event)

    controller.setActiveTool(random_tool)
    random_tool.event.reset_mock() #  We don't care about activation events.
    controller.event(event)
    # The camera tool should not get an extra call
    camera_tool.event.assert_called_once_with(event)
    # But the active tool should have gotten one
    random_tool.event.assert_called_once_with(event)

    controller.setSelectionTool(selection_tool)
    controller.event(event)
    # The camera tool should not get an extra call
    camera_tool.event.assert_called_once_with(event)
    # The active tool should not get an extra call
    random_tool.event.assert_called_once_with(event)
    # But the selection tool should have gotten one
    selection_tool.event.assert_called_once_with(event)


def test_setSelectionTool(application):
    controller = Controller(application)
    controller.getTool = MagicMock()

    controller.setSelectionTool("beep")

    controller.getTool.assert_called_once_with("beep")


def test_deleteAllNodesWithMeshData(application):
    controller = Controller(application)

    node_1 = SceneNode()
    node_1.setMeshData(MeshData())
    node_1.setSelectable(True)

    node_2 = SceneNode()

    node_3 = SceneNode()
    node_3.setMeshData(MeshData())

    controller.getScene().getRoot().addChild(node_1)
    controller.getScene().getRoot().addChild(node_2)
    controller.getScene().getRoot().addChild(node_3)

    controller.deleteAllNodesWithMeshData()

    children = controller.getScene().getRoot().getAllChildren()
    assert node_1 not in children  # Should be removed because it's selectable and has a mesh.
    assert node_2 in children  # Has no mesh.
    assert node_3 in children  # Has a mesh, but isn't selectable.


def test_deleteAllNodesWithMeshData_toolsDisabled(application):
    controller = Controller(application)

    node_1 = SceneNode()
    node_1.setMeshData(MeshData())
    node_1.setSelectable(True)

    controller.getScene().getRoot().addChild(node_1)
    controller.getToolsEnabled = MagicMock(return_value = False)

    controller.deleteAllNodesWithMeshData()

    children = controller.getScene().getRoot().getAllChildren()
    assert node_1 in children  # Should still be in there, because the tools are not active.
