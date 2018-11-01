# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
import os.path
from typing import Optional

from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QVariant, QUrl

from UM.Application import Application
from UM.PluginRegistry import PluginRegistry
from UM.View.View import View


class ActiveViewProxy(QObject):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self._active_view = None  # type: Optional[View]
        Application.getInstance().getController().activeViewChanged.connect(self._onActiveViewChanged)
        self._onActiveViewChanged()
        
    activeViewChanged = pyqtSignal()
    
    @pyqtProperty(QUrl, notify = activeViewChanged)
    def activeViewPanel(self) -> QUrl:
        if not self._active_view:
            return QUrl()

        try:
            panel_file = PluginRegistry.getInstance().getMetaData(self._active_view.getPluginId())["view"]["view_panel"]
        except KeyError:
            return QUrl()

        plugin_path = PluginRegistry.getInstance().getPluginPath(self._active_view.getPluginId())
        if plugin_path:
            return QUrl.fromLocalFile(os.path.join(plugin_path, panel_file))

        return QUrl()

    ##  Allows trigger backend function from QML, example: UM.ActiveTool.triggerAction("layFlat")
    #
    #   \param action The function name which will be triggered.
    #   \param data The argument which will pass to the action function
    @pyqtSlot(str, QVariant)
    def triggerAction(self, action_name: str, data: QVariant) -> None:
        if not self._active_view:
            return

        action = getattr(self._active_view, action_name)
        if action:
            action(data)

    @pyqtProperty(bool, notify = activeViewChanged)
    def valid(self) -> bool:
        return self._active_view is not None

    def _onActiveViewChanged(self) -> None:
        self._active_view = Application.getInstance().getController().getActiveView()
        self.activeViewChanged.emit()


def createActiveViewProxy(engine, script_engine):
    return ActiveViewProxy()
