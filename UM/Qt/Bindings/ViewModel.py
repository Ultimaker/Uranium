from PyQt5.QtCore import QAbstractListModel, QCoreApplication, Qt, QVariant

from UM.Qt.ListModel import ListModel
from UM.Application import Application

class ViewModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    ActiveRole = Qt.UserRole + 3

    def __init__(self, parent = None):
        super().__init__(parent)
        self._controller = Application.getInstance().getController()
        self._controller.viewsChanged.connect(self._onViewsChanged)
        self._onViewsChanged()

        self.addRoleName(self.IdRole, 'id')
        self.addRoleName(self.NameRole, 'name')
        self.addRoleName(self.ActiveRole, 'active')

    def _onViewsChanged(self):
        self.clear()
        views = self._controller.getAllViews()

        for name in views:
            metaData = Application.getInstance().getPluginRegistry().getMetaData(name)

            # Skip view modes that are marked as not visible
            if 'visible' in metaData and not metaData['visible']:
                continue

            # Skip tools that are marked as not visible for this application
            appName = Application.getInstance().getApplicationName()
            if appName in metaData and 'visible' in metaData[appName] and not metaData[appName]['visible']:
                continue

            # Optional metadata elements
            currentView = self._controller.getActiveView()
            self.appendItem({ 'id': name, 'name': metaData.get('displayName', name), 'active': name == currentView })

        self.sort(lambda t: t['name'])
