# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import sys
import os.path
import signal
import traceback

from PyQt5.QtCore import QObject, QUrl, pyqtSlot, pyqtProperty, pyqtSignal
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt5.QtWidgets import QApplication

import UM.Resources
import UM.Settings
import UM.Settings.Models

class DefinitionLoader(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._error_text = ""
        self._metadata_text = ""

    @pyqtSlot("QUrl", result = str)
    def load(self, file_path):
        try:
            definition = UM.Settings.DefinitionContainer(file_path.fileName())

            dirname = os.path.dirname(file_path.toLocalFile())
            UM.Resources.Resources.addSearchPath(dirname)
            UM.Resources.Resources.addSearchPath(os.path.realpath(os.path.join(dirname, "..")))

            with open(file_path.toLocalFile()) as data:
                definition.deserialize(data.read())

            self._metadata_text = ""
            for key, value in definition.metaData.items():
                self._metadata_text += "<b>{0}:</b> {1}<br/>".format(key, value)
            self.metaDataTextChanged.emit()

            UM.Settings.ContainerRegistry.getInstance().addContainer(definition)
            return definition.id
        except Exception as e:
            self._error_text = "An exception occurred loading file {0}:\n".format(file_path)
            self._error_text += str(e)
            self._error_text += traceback.format_exc()
            self.errorTextChanged.emit()
            return None


    errorTextChanged = pyqtSignal()
    @pyqtProperty(str, notify=errorTextChanged)
    def errorText(self):
        return self._error_text

    metaDataTextChanged = pyqtSignal()
    @pyqtProperty(str, notify=metaDataTextChanged)
    def metaDataText(self):
        return self._metadata_text

signal.signal(signal.SIGINT, signal.SIG_DFL)

file_name = None
if len(sys.argv) > 1:
    file_name = sys.argv[1]
    del sys.argv[1]

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()

qmlRegisterType(DefinitionLoader, "Example", 1, 0, "DefinitionLoader")
qmlRegisterType(UM.Settings.Models.SettingDefinitionsModel, "Example", 1, 0, "SettingDefinitionsModel")

if file_name:
    engine.rootContext().setContextProperty("open_file", QUrl.fromLocalFile(file_name))

engine.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.qml"))
app.exec_()
