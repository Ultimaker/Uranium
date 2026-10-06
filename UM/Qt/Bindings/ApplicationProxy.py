# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtProperty, pyqtSignal
import PyQt6.QtWidgets

from UM.Application import Application
from UM.Decorators import deprecated

class ApplicationProxy(QObject):
    currentKeyboardModifiersChanged = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self._application = Application.getInstance()

        PyQt6.QtWidgets.QApplication.instance().currentKeyboardModifiersChanged.connect(self.currentKeyboardModifiersChanged)

    @pyqtProperty(str, constant = True)
    @deprecated("Will be removed in major SDK release, use CuraApplication.version in place of UM.Application.version", since="5.7.0")
    def version(self):
        return self._application.getVersion()

    @pyqtProperty(Qt.KeyboardModifier, notify=currentKeyboardModifiersChanged)
    def currentKeyboardModifiers(self):
        return PyQt6.QtWidgets.QApplication.instance().currentKeyboardModifiers
