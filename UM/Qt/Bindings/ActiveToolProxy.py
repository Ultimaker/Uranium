# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QUrl

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry

import os.path

class ActiveToolProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._active_tool = None
        Application.getInstance().getController().activeToolChanged.connect(self._onActiveToolChanged)
        self._onActiveToolChanged()

    activeToolChanged = pyqtSignal()
    propertyChanged = pyqtSignal()

    @pyqtProperty(bool, notify = activeToolChanged)
    def valid(self):
        return self._active_tool != None

    @pyqtProperty(QUrl, notify = activeToolChanged)
    def activeToolPanel(self):
        if not self._active_tool:
            return QUrl()

        try:
            panel_file = PluginRegistry.getInstance().getMetaData(self._active_tool.getPluginId())["tool"]["tool_panel"]
        except KeyError:
            return QUrl()

        return QUrl.fromLocalFile(os.path.join(PluginRegistry.getInstance().getPluginPath(self._active_tool.getPluginId()), panel_file))

    @pyqtSlot(str)
    def triggerAction(self, action):
        if not self._active_tool:
            return

        action = getattr(self._active_tool, action)
        if action:
            action()

    @pyqtSlot(str, result = "QVariant")
    def getProperty(self, property):
        if not self._active_tool:
            return None

        property_getter = getattr(self._active_tool, "get" + property)
        if property_getter:
            return property_getter()

        if hasattr(self._active_tool, property):
            return getattr(self._active_tool, property)

        return None


    @pyqtSlot(str, "QVariant")
    def setProperty(self, property, value):
        if not self._active_tool:
            return

        option_setter = getattr(self._active_tool, "set" + property)
        if option_setter:
            option_setter(value)

        if hasattr(self._active_tool, property):
            setattr(self._active_tool, property, value)

    def _onPropertyChanged(self):
        self.propertyChanged.emit()

    def _onActiveToolChanged(self):
        self._active_tool = Application.getInstance().getController().getActiveTool()
        if self._active_tool is not None:
            self._active_tool.propertyChanged.connect(self._onPropertyChanged)
        self.activeToolChanged.emit()

def createActiveToolProxy(engine, script_engine):
    return ActiveToolProxy()
