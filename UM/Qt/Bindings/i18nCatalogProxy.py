# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QUrl

from UM.i18n import i18nCatalog

class i18nCatalogProxy(QObject): # [CodeStyle: Ultimaker code style requires classes to start with a upper case. But i18n is lower case by convention.]
    def __init__(self, parent = None):
        super().__init__()

        self._name = None
        self._catalog = None

    def setName(self, name):
        if name != self._name:
            self._catalog = i18nCatalog(name)
            self.nameChanged.emit()

    nameChanged = pyqtSignal()
    
    @pyqtProperty(str, fset = setName, notify = nameChanged)
    def name(self):
        return self._name

    @pyqtSlot(str, result = str)
    def i18n(self, message):
        return self._catalog.i18n(message)

    @pyqtSlot(str, str, result = str)
    def i18nc(self, context, message):
        return self._catalog.i18nc(context, message)

    @pyqtSlot(str, str, int, result = str)
    def i18np(self, single, multiple, counter):
        return self._catalog.i18np(single, multiple, counter)

    @pyqtSlot(str, str, str, int, result = str)
    def i18ncp(self, context, single, multiple, counter):
        return self._catalog.i18ncp(context, single, multiple, counter)
