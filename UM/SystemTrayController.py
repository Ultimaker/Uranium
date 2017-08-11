#!/usr/bin/env python3

import os
# import sys
from PyQt5 import QtGui, QtWidgets


## The classs provides functionalty to display messages in system tray
class SystemTrayController(QtWidgets.QSystemTrayIcon):
    _iconPath = None
    _instance = None
    _checkStateMethod = None
    _tempPath = ["cura", "icons", "cura-32.png"]

    # Use only for testing
    # _app = QtWidgets.QApplication(sys.argv)

    def __init__(self, parent=None):
        self.__setIconPath()
        QtWidgets.QSystemTrayIcon.__init__(self, QtGui.QIcon(self._iconPath), parent)
        self.show()
        # Do not show the icon in systemTray
        self.setVisible(False)

    def __setIconPath(self):
        dirPath = os.path.dirname(os.path.realpath(__file__))
        dirPaths = dirPath.split(os.sep)
        dirPaths = dirPaths[:-2 or None]
        dirPaths.extend(self._tempPath)
        self._iconPath = os.path.join(os.path.sep, *dirPaths)

    @classmethod
    def initSystemTrayController(cls, checkMethod):
        if not cls._instance:
            cls._checkStateMethod = checkMethod
            cls._instance = SystemTrayController()

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            # Check whether the instance exists, it will help prevent exception.
            # Note: the object should be initialized in initSystemTrayController
            cls._instance = SystemTrayController()
        return cls._instance

    def showMessage(self, title, message):
        if self._checkStateMethod is not None and self._checkStateMethod():
            # it is a trick, to show only the toast message and hide immediately icon in systemTray
            self.setVisible(True)
            super().showMessage(title, message, QtGui.QIcon(self._iconPath))
            self.setVisible(False)
