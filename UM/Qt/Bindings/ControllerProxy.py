# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty

from UM.Application import Application
from UM.Decorators import deprecated
from UM.Scene.Selection import Selection
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
from UM.Operations.GroupedOperation import GroupedOperation


class ControllerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._controller = Application.getInstance().getController()
        self._controller.contextMenuRequested.connect(self._onContextMenuRequested)
        self._selection_pass = None
        self._tools_enabled = True

        # bind needed signals
        self._controller.toolOperationStarted.connect(self._onToolOperationStarted)
        self._controller.toolOperationStopped.connect(self._onToolOperationStopped)
        self._controller.activeStageChanged.connect(self._onActiveStageChanged)
        self._controller.activeViewChanged.connect(self._onActiveViewChanged)

    toolsEnabledChanged = pyqtSignal()
    activeStageChanged = pyqtSignal()
    activeViewChanged = pyqtSignal()

    @pyqtProperty(bool, notify = toolsEnabledChanged)
    def toolsEnabled(self):
        return self._tools_enabled

    @pyqtProperty(QObject, notify = activeStageChanged)
    def activeStage(self):
        return self._controller.getActiveStage()

    @pyqtSlot(str)
    def setActiveView(self, view):
        self._controller.setActiveView(view)

    @pyqtProperty(QObject, notify = activeViewChanged)
    def activeView(self):
        return self._controller.getActiveView()

    @pyqtSlot(str)
    def setActiveStage(self, stage):
        self._controller.setActiveStage(stage)

    @pyqtSlot(str)
    def setActiveTool(self, tool):
        self._controller.setActiveTool(tool)

    @pyqtSlot()
    def removeSelection(self):
        if not Selection.hasSelection():
            return

        op = GroupedOperation()
        for node in Selection.getAllSelectedObjects():
            op.addOperation(RemoveSceneNodeOperation(node))
        op.push()
        Selection.clear()

    @pyqtSlot(str, int)
    def setCameraRotation(self, coordinate: str, angle: int) -> None:
        self._controller.setCameraRotation(coordinate, angle)

    @pyqtSlot(int, int, int)
    def setCameraPosition(self, x_position: int = 0, y_position: int = 0, z_position: int = 0) -> None:
        self._controller.setCameraPosition(x_position, y_position, z_position)

    @pyqtSlot(int, int, int)
    def setLookAtPosition(self, x_look_at_position: int = 0, y_look_at_position: int = 0, z_look_at_position: int = 0) -> None:
        self._controller.setLookAtPosition(x_look_at_position, y_look_at_position, z_look_at_position)

    @pyqtSlot(float)
    def setCameraZoomFactor(self, camera_zoom_factor: float = 0) -> None:
        self._controller.setCameraZoomFactor(camera_zoom_factor)

    @pyqtSlot(str)
    def setCameraOrigin(self, coordinate: str) -> None:
        """Changes the position of the origin of the camera.
        :param coordinate: The new origin of the camera. Use either:
                           "home": The centre of the build plate.
                           "3d": The centre of the build volume.
        """

        self._controller.setCameraOrigin(coordinate)

    contextMenuRequested = pyqtSignal("quint64", arguments=["objectId"])

    def _onContextMenuRequested(self, x, y):
        if not self._selection_pass:
            self._selection_pass =  Application.getInstance().getRenderer().getRenderPass("selection")

        id = self._selection_pass.getIdAtPosition(x, y)

        if id:
            self.contextMenuRequested.emit(id)
        else:
            self.contextMenuRequested.emit(0)

    def _onToolOperationStarted(self, tool):
        self._tools_enabled = False
        self._controller.setToolsEnabled(False)
        self.toolsEnabledChanged.emit()

    def _onToolOperationStopped(self, tool):
        self._tools_enabled = True
        self._controller.setToolsEnabled(True)
        self.toolsEnabledChanged.emit()

    def _onActiveStageChanged(self):
        self.activeStageChanged.emit()

    def _onActiveViewChanged(self):
        self.activeViewChanged.emit()
