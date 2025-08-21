# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
import os
from typing import Any

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty, QUrl, QVariant

from UM.Application import Application
from UM.Scene.Selection import Selection
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
from UM.Operations.GroupedOperation import GroupedOperation

from . import ContainerProxy
from ...Decorators import deprecated
from ...Logger import Logger
from ...PluginRegistry import PluginRegistry


class ControllerProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)
        self._controller = Application.getInstance().getController()
        self._controller.contextMenuRequested.connect(self._onContextMenuRequested)
        self._selection_pass = None
        self._tools_enabled = True

        self._active_tool = None
        self._properties = {}
        Application.getInstance().getController().activeToolChanged.connect(self._onActiveToolChanged)
        self._onActiveToolChanged()


        self._properties_proxy = ContainerProxy.ContainerProxy(self._properties)

        # bind needed signals
        self._controller.toolOperationStarted.connect(self._onToolOperationStarted)
        self._controller.toolOperationStopped.connect(self._onToolOperationStopped)
        self._controller.activeStageChanged.connect(self._onActiveStageChanged)
        self._controller.activeViewChanged.connect(self._onActiveViewChanged)

    toolsEnabledChanged = pyqtSignal()
    activeStageChanged = pyqtSignal()
    activeViewChanged = pyqtSignal()
    activeToolChanged = pyqtSignal()

    @pyqtProperty(bool, notify = toolsEnabledChanged)
    def toolsEnabled(self):
        return self._tools_enabled

    @pyqtProperty(QObject, notify = activeStageChanged)
    def activeStage(self):
        return self._controller.getActiveStage()

    @pyqtSlot(str)
    @deprecated("Active view should be set through the active Stage", since="5.11.0")
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


    @pyqtProperty(bool, notify = activeToolChanged)
    def valid(self):
        return self._active_tool != None

    @pyqtProperty(QUrl, notify = activeToolChanged)
    def activeToolPanel(self):
        if not self._active_tool:
            return QUrl()
        try:
            panel_file = self._active_tool.getMetaData()["tool_panel"]
        except KeyError:
            return QUrl()

        return QUrl.fromLocalFile(os.path.join(PluginRegistry.getInstance().getPluginPath(self._active_tool.getPluginId()), panel_file))

    @pyqtSlot(str)
    def triggerAction(self, action):
        if not self._active_tool:
            return
        if not hasattr(self._active_tool, action):
            Logger.log("w", "Trying to call non-existing action {action} of tool {tool}.".format(action = action, tool = self._active_tool.getPluginId()))
            return

        action = getattr(self._active_tool, action)
        if action:
            action()

    @pyqtSlot(str, QVariant)
    def triggerActionWithData(self, action: str, data: Any):
        """Triggers one of the tools' actions and provides additional parameters to the action.

        The additional data is passed as a parameter to the function call of the
        action.
        :param action: The action to trigger.
        :param data: The additional data to call
        """

        if not self._active_tool:
            return
        if not hasattr(self._active_tool, action):
            Logger.log("w", "Trying to call non-existing action {action} of tool {tool}.".format(action = action, tool = self._active_tool.getPluginId()))
            return

        if hasattr(self._active_tool, action):
            getattr(self._active_tool, action)(data)

    propertiesChanged = pyqtSignal()
    @pyqtProperty(QObject, notify = propertiesChanged)
    def properties(self):
        return self._properties_proxy

    @pyqtSlot()
    def forceUpdate(self):
        self._updateProperties()

    @pyqtSlot(str, "QVariant")
    def setProperty(self, property, value):
        if not self._active_tool:
            return
        if hasattr(self._active_tool, "set" + property):
            option_setter = getattr(self._active_tool, "set" + property)
            if option_setter:
                try:
                    option_setter(value)
                except Exception as e:
                    Logger.logException("e", f"Unable to set value '{value}' to property '{property}'.")

        if hasattr(self._active_tool, property):
            setattr(self._active_tool, property, value)

    def _onPropertyChanged(self):
        self._updateProperties()

    def _onActiveToolChanged(self):
        if self._active_tool:
            self._active_tool.propertyChanged.disconnect(self._onPropertyChanged)

        self._active_tool = Application.getInstance().getController().getActiveTool()
        if self._active_tool is not None:
            self._active_tool.propertyChanged.connect(self._onPropertyChanged)
            self._updateProperties()

        self.activeToolChanged.emit()

    def _updateProperties(self):
        self._properties.clear()

        for name in self._active_tool.getExposedProperties():
            property_getter = getattr(self._active_tool, "get" + name)
            if property_getter:
                self._properties[name] = property_getter()

            if hasattr(self._active_tool, name):
                self._properties[name] = getattr(self._active_tool, name)

        self.propertiesChanged.emit()
