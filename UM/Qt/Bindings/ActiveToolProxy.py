# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any
from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QUrl, QVariant

from UM.Application import Application
from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry

from . import ContainerProxy

import os.path


class ActiveToolProxy(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._active_tool = None
        self._properties = {}
        Application.getInstance().getController().activeToolChanged.connect(self._onActiveToolChanged)
        self._onActiveToolChanged()


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
