from PyQt5.QtCore import Qt, QCoreApplication

from Cura.Qt.ListModel import ListModel

class ToolModel(ListModel):
    NameRole = Qt.UserRole + 1

    def __init__(self, parent = None):
        super().__init__(parent)

        self._controller = QCoreApplication.instance().getController()
        self._controller.toolsChanged.connect(self._onToolsChanged)
        self._onToolsChanged()

    def roleNames(self):
        return { self.NameRole: 'name' }

    def _onToolsChanged(self):
        self.clear()

        tools = self._controller.getAllTools()
        for name in tools:
            self.appendItem({ 'name': name })

