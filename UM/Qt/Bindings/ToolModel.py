from PyQt5.QtCore import Qt

from UM.Application import Application

from UM.Qt.ListModel import ListModel

class ToolModel(ListModel):
    NameRole = Qt.UserRole + 1
    IconRole = Qt.UserRole + 2
    ToolActiveRole = Qt.UserRole + 3
    DescriptionRole = Qt.UserRole + 4

    def __init__(self, parent = None):
        super().__init__(parent)

        self._controller = Application.getInstance().getController()
        self._controller.toolsChanged.connect(self._onToolsChanged)
        self._controller.activeToolChanged.connect(self._onActiveToolChanged)
        self._onToolsChanged()
        
        self.addRoleName(self.NameRole, 'name')
        self.addRoleName(self.IconRole, 'icon')
        self.addRoleName(self.ToolActiveRole, 'active')
        self.addRoleName(self.DescriptionRole, 'description')

    def _onToolsChanged(self):
        self.clear()

        tools = self._controller.getAllTools()
        for name in tools:
            toolMetaData = Application.getInstance().getPluginRegistry().getMetaData(name)

            # Skip tools that are marked as not visible
            if 'visible' in toolMetaData and not toolMetaData['visible']:
                continue

            # Skip tools that are marked as not visible for this application
            appName = Application.getInstance().getApplicationName()
            if appName in toolMetaData and 'visible' in toolMetaData[appName] and not toolMetaData[appName]['visible']:
                continue

            # Optional metadata elements
            description = toolMetaData['description'] if 'description' in toolMetaData else ''
            iconName = toolMetaData['icon'] if 'icon' in toolMetaData else 'default.png'

            self.appendItem({ 'name': name, 'icon': iconName, 'active': False, 'description': description })

    def _onActiveToolChanged(self):
        activeTool = self._controller.getActiveTool()

        for index, value in enumerate(self.items):
            if self._controller.getTool(value['name']) == activeTool:
                self.setProperty(index, 'active', True)
            else:
                self.setProperty(index, 'active', False)
