from PyQt5.QtCore import Qt, QCoreApplication

from Cura.Qt.ListModel import ListModel

class ToolModel(ListModel):
    NameRole = Qt.UserRole + 1
    IconRole = Qt.UserRole + 2
    ToolActiveRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)

        self._controller = QCoreApplication.instance().getController()
        self._controller.toolsChanged.connect(self._onToolsChanged)
        self._controller.activeToolChanged.connect(self._onActiveToolChanged)
        self._onToolsChanged()

    def roleNames(self):
        return { self.NameRole: 'name', self.IconRole: 'icon', self.ToolActiveRole: 'active' }

    def _onToolsChanged(self):
        self.clear()

        tools = self._controller.getAllTools()
        for name in tools:
            self.appendItem({ 'name': name, 'icon': tools[name].getIconName(), 'active': False })

    def _onActiveToolChanged(self):
        activeTool = self._controller.getActiveTool()

        for index, value in enumerate(self.items):
            if self._controller.getTool(value['name']) == activeTool:
                self.setProperty(index, 'active', True)
            else:
                self.setProperty(index, 'active', False)
