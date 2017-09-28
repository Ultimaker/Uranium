# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QUrl

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry

from . import ContainerProxy

import os.path

class ActiveToolProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._active_tool = None
        Application.getInstance().getController().activeToolChanged.connect(self._onActiveToolChanged)
        self._onActiveToolChanged()

        self._properties = { }
        self._properties_proxy = ContainerProxy.ContainerProxy(self._properties)

    activeToolChanged = pyqtSignal()

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
                option_setter(value)

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

def createActiveToolProxy(engine, script_engine):
    return ActiveToolProxy()
