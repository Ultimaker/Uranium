from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject

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

    @pyqtProperty(bool, notify = activeToolChanged)
    def valid(self):
        return self._active_tool != None

    @pyqtProperty(str, notify = activeToolChanged)
    def activeToolPanel(self):
        if not self._active_tool:
            return ""

        try:
            panel_file = PluginRegistry.getInstance().getMetaData(self._active_tool.getPluginId())['tool']['tool_panel']
        except KeyError:
            return ""

        return os.path.join(PluginRegistry.getInstance().getPluginPath(self._active_tool.getPluginId()), panel_file)

    @pyqtSlot(str)
    def triggerAction(self, action):
        if not self._active_tool:
            return

        action = getattr(self._active_tool, action)
        if action:
            action()

    def _onActiveToolChanged(self):
        self._active_tool = Application.getInstance().getController().getActiveTool()
        self.activeToolChanged.emit()

def createActiveToolProxy(engine, script_engine):
    return ActiveToolProxy()
