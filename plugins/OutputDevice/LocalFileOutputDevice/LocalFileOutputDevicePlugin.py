# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import os.path

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from UM.Application import Application
from UM.Preferences import Preferences
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin
from UM.OutputDevice.OutputDevice import OutputDevice
from UM.OutputDevice.OutputDeviceError import ErrorCodes, WriteRequestFailedError

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

        file_types = []
        selected_filter = None
        last_used_filter = Preferences.getInstance().getValue("local_file/last_used_type")

        for ext, desc in Application.getInstance().getMeshFileHandler().getSupportedFileTypesWrite().items():
            file_types.append("{0} (*.{1})".format(desc, ext))
            if ext == last_used_filter:
                selected_filter = "{0} (*.{1})".format(desc, ext)

        file_types.sort()

        dialog.setNameFilters(file_types)
        if selected_filter != None:
            dialog.selectNameFilter(selected_filter)

        dialog.restoreState(Preferences.getInstance().getValue("local_file/dialog_state"))

        if not dialog.exec_():
            raise WriteRequestFailedError(ErrorCodes.UserCanceledError, "Cancelled by user")

        Preferences.getInstance().setValue("local_file/dialog_state", dialog.saveState())

        for ext, desc in Application.getInstance().getMeshFileHandler().getSupportedFileTypesWrite().items():
            if "{0} (*.{1})".format(desc, ext) == dialog.selectedNameFilter():
                Preferences.getInstance().setValue("local_file/last_used_type", ext)

        file_name = dialog.selectedFiles()[0]

        if os.path.exists(file_name):
            result = QMessageBox.question(None, catalog.i18n("File Already Exists"), catalog.i18n("The file {0} already exists. Are you sure you want to overwrite it?"))
            if result == QMessageBox.No:
                raise WriteRequestFailedError(ErrorCodes.UserCanceledError, "Cancelled by user")

        print(file_name)
        #Application.getInstance().getMeshFileHandler().write(file_name, node)


