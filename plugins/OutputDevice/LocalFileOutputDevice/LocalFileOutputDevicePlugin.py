# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os.path
import sys

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from UM.Application import Application
from UM.Preferences import Preferences
from UM.Logger import Logger
from UM.Mesh.WriteMeshJob import WriteMeshJob
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin
from UM.OutputDevice.OutputDevice import OutputDevice
from UM.OutputDevice.OutputDeviceError import UserCancelledError, PermissionDeniedError, WriteRequestFailedError

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

class LocalFileOutputDevicePlugin(OutputDevicePlugin):
    def __init__(self):
        super().__init__()

        Preferences.getInstance().addPreference("local_file/last_used_type", "")
        Preferences.getInstance().addPreference("local_file/dialog_state", "")

    def start(self):
        self.getOutputDeviceManager().addOutputDevice(LocalFileOutputDevice())

    def stop(self):
        self.getOutputDeviceManager().removeOutputDevice("local_file")

class LocalFileOutputDevice(OutputDevice):
    def __init__(self):
        super().__init__("local_file")

        self.setName(catalog.i18nc("Local File Output Device Name", "Local File"))
        self.setShortDescription(catalog.i18n("Save to File"))
        self.setDescription(catalog.i18n("Save to File"))
        self.setIconName("save")

    def requestWrite(self, node):
        dialog = QFileDialog()
        dialog.setWindowTitle(catalog.i18n("Save to File"))
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        # Ensure platform never ask for overwrite confirmation since we do this ourselves
        dialog.setOption(QFileDialog.DontConfirmOverwrite)

        filters = []
        selected_filter = None
        last_used_type = Preferences.getInstance().getValue("local_file/last_used_type")

        file_types = Application.getInstance().getMeshFileHandler().getSupportedFileTypesWrite()
        file_types.sort(key = lambda k: k["description"])

        for item in file_types:
            type_filter = "{0} (*.{1})".format(item["description"], item["extension"])
            filters.append(type_filter)
            if last_used_type in item["mime_types"]:
                selected_filter = type_filter

        dialog.setNameFilters(filters)
        if selected_filter != None:
            dialog.selectNameFilter(selected_filter)

        dialog.restoreState(Preferences.getInstance().getValue("local_file/dialog_state"))

        if not dialog.exec_():
            raise UserCancelledError()

        Preferences.getInstance().setValue("local_file/dialog_state", dialog.saveState())

        selected_type = file_types[filters.index(dialog.selectedNameFilter())]
        Preferences.getInstance().setValue("local_file/last_used_type", selected_type["mime_types"][0])

        file_name = dialog.selectedFiles()[0]

        if os.path.exists(file_name):
            result = QMessageBox.question(None, catalog.i18n("File Already Exists"), catalog.i18n("The file {0} already exists. Are you sure you want to overwrite it?"))
            if result == QMessageBox.No:
                raise WriteRequestFailedError(ErrorCodes.UserCanceledError, "Cancelled by user")

        self.writeStarted.emit(self)
        mesh_writer = Application.getInstance().getMeshFileHandler().getWriter(selected_type["id"])
        try:
            Logger.log("d", "Writing to Local File %s", file_name)
            stream = open(file_name, "w")
            job = WriteMeshJob(mesh_writer, stream, node)
            #job.progress.connect(self._onJobProgress)
            job.finished.connect(self._onWriteJobFinished)
            job.start()
        except PermissionError:
            raise PermissionDeniedError().with_traceback(sys.exc_info()[2])
        except OSError:
            raise WriteRequestFailedError().with_traceback(sys.exc_info()[2])

    def _onJobProgress(self, job):
        self.writeProgress.emit(job.getProgress())

    def _onWriteJobFinished(self, job):
        self.writeFinished.emit(self)
        if job.getResult():
            self.writeSuccess.emit(self)
        else:
            self.writeError.emit(self)
        job.getStream().close()
