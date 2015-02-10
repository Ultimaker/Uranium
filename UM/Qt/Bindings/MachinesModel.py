from UM.Qt.ListModel import ListModel

from PyQt5.QtCore import Qt

class MachinesModel(ListModel):
    NameRole = Qt.UserRole + 1

    def __init__(self):
        super().__init__()

        self.addRoleName(self.NameRole, 'name')

        for i in range(10):
            self.appendItem({'name': "Ultimaker {0}".format(i)})

