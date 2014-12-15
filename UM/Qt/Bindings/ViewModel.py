from PyQt5.QtCore import QAbstractListModel, QCoreApplication, Qt, QVariant

from UM.Qt.ListModel import ListModel

class ViewModel(ListModel):
    TextRole = Qt.UserRole + 1

    def __init__(self, parent = None):
        super().__init__(parent)
        self._controller = QCoreApplication.instance().getController()
        self._controller.viewsChanged.connect(self._onViewsChanged)
        self._onViewsChanged()

    def roleNames(self):
        return { self.TextRole: 'text' }

    def _onViewsChanged(self):
        self.clear()
        views = self._controller.getAllViews()

        for name in views:
            self.appendItem({ 'text': name })

        self.sort(lambda t: t['text'])
