# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import sys
import os.path
import signal
import traceback

from PyQt5.QtCore import QObject, QUrl, pyqtSlot, pyqtProperty, pyqtSignal
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType
from PyQt5.QtWidgets import QApplication

import UM.Resources
import UM.Settings

import DefinitionTreeModel

class DefinitionLoader(QObject):
    def __init__(self, parent = None):
        super().__init__(parent)

        self._metadata = {}
        self._definition_id = ""

    @pyqtSlot("QUrl", result = str)
    def load(self, file_path):
        try:
            definition = UM.Settings.DefinitionContainer(file_path.fileName())

            dirname = os.path.dirname(file_path.toLocalFile())
            UM.Resources.Resources.addSearchPath(dirname)
            UM.Resources.Resources.addSearchPath(os.path.realpath(os.path.join(dirname, "..")))

            with open(file_path.toLocalFile(), encoding = "utf-8") as data:
                definition.deserialize(data.read())

            self._metadata = dict(definition.metaData)
            self.metaDataChanged.emit()

            UM.Settings.ContainerRegistry.ContainerRegistry.getInstance().addContainer(definition)
            self._definition_id = definition.id
            self.loaded.emit()
        except Exception as e:
            error_text = "An exception occurred loading file {0}:\n".format(file_path)
            error_text += str(e)
            error_text += traceback.format_exc()
            self.error.emit(error_text)

    loaded = pyqtSignal()
    error = pyqtSignal(str, arguments=["errorText"])

    metaDataChanged = pyqtSignal()
    @pyqtProperty("QVariantMap", notify=metaDataChanged)
    def metaData(self):
        return self._metadata

    @pyqtProperty(str, notify=loaded)
    def definitionId(self):
        return self._definition_id

signal.signal(signal.SIGINT, signal.SIG_DFL)

file_name = None
if len(sys.argv) > 1:
    file_name = sys.argv[1]
    del sys.argv[1]

app = QApplication(sys.argv)
engine = QQmlApplicationEngine()

qmlRegisterType(DefinitionLoader, "Example", 1, 0, "DefinitionLoader")
qmlRegisterType(DefinitionTreeModel.DefinitionTreeModel, "Example", 1, 0, "DefinitionTreeModel")

if file_name:
    engine.rootContext().setContextProperty("open_file", QUrl.fromLocalFile(file_name))

engine.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.qml"))
app.exec_()
