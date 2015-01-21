from PyQt5.QtCore import Qt

from UM.Application import Application
from UM.Qt.ListModel import ListModel

class PluginsModel(ListModel):
    NameRole = Qt.UserRole + 1
    
    def __init__(self, parent = None):
        super().__init__(parent)