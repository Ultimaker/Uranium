# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from UM.Application import Application
from UM.FileHandler.WriteFileJob import WriteFileJob
from UM.Logger import Logger
from UM.Mesh.MeshWriter import MeshWriter
from UM.Message import Message
from UM.OutputDevice import OutputDeviceError
from UM.OutputDevice.OutputDevice import OutputDevice
from UM.i18n import i18nCatalog

catalog = i18nCatalog("uranium")


class LocalFileOutputDevice(OutputDevice):
    """Implements an OutputDevice that supports saving to arbitrary local files."""

    def __init__(self):
        super().__init__("local_file")

        self.setName(catalog.i18nc("@item:inmenu", "Local File"))
        self.setShortDescription(catalog.i18nc("@action:button Preceded by 'Ready to'.", "Save to File"))
        self.setDescription(catalog.i18nc("@info:tooltip", "Save to File"))
        self.setIconName("save")

        self._writing = False

    def requestWrite(self, nodes, file_name = None, limit_mimetypes = None, file_handler = None, **kwargs):
        """Request the specified nodes to be written to a file.

        :param nodes: A collection of scene nodes that should be written to the
        file.
        :param file_name: A suggestion for the file name to write
        to. Can be freely ignored if providing a file name makes no sense.
        :param limit_mimetypes: Should we limit the available MIME types to the
        MIME types available to the currently active machine?
        :param kwargs: Keyword arguments.
        """

        if self._writing:
            raise OutputDeviceError.DeviceBusyError()

        # Set up and display file dialog
        dialog = QFileDialog()

        dialog.setWindowTitle(catalog.i18nc("@title:window", "Save to File"))
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)

        # Ensure platform never ask for overwrite confirmation since we do this ourselves
        dialog.setOption(QFileDialog.DontConfirmOverwrite)

        if sys.platform == "linux" and "KDE_FULL_SESSION" in os.environ:
            dialog.setOption(QFileDialog.DontUseNativeDialog)

        filters = []
        mime_types = []
        selected_filter = None

        if "preferred_mimetypes" in kwargs and kwargs["preferred_mimetypes"] is not None:
            preferred_mimetypes = kwargs["preferred_mimetypes"]
        else:
            preferred_mimetypes = Application.getInstance().getPreferences().getValue("local_file/last_used_type")
        preferred_mimetype_list = preferred_mimetypes.split(";")

        if not file_handler:
            file_handler = Application.getInstance().getMeshFileHandler()

        file_types = file_handler.getSupportedFileTypesWrite()

        file_types.sort(key = lambda k: k["description"])
        if limit_mimetypes:
            file_types = list(filter(lambda i: i["mime_type"] in limit_mimetypes, file_types))

        file_types = [ft for ft in file_types if not ft["hide_in_file_dialog"]]

        if len(file_types) == 0:
            Logger.log("e", "There are no file types available to write with!")
            raise OutputDeviceError.WriteRequestFailedError(catalog.i18nc("@info:warning", "There are no file types available to write with!"))

        # Find the first available preferred mime type
        preferred_mimetype = None
        for mime_type in preferred_mimetype_list:
            if any(ft["mime_type"] == mime_type for ft in file_types):
                preferred_mimetype = mime_type
                break

        extension_added = False
        for item in file_types:
            type_filter = "{0} (*.{1})".format(item["description"], item["extension"])
            filters.append(type_filter)
            mime_types.append(item["mime_type"])
            if preferred_mimetype == item["mime_type"]:
                selected_filter = type_filter
                if file_name and not extension_added:
                    extension_added = True
                    file_name += "." + item["extension"]

        # CURA-6411: This code needs to be before dialog.selectFile and the filters, because otherwise in macOS (for some reason) the setDirectory call doesn't work.
        stored_directory = Application.getInstance().getPreferences().getValue("local_file/dialog_save_path")
        dialog.setDirectory(stored_directory)

        # Add the file name before adding the extension to the dialog
        if file_name is not None:
            dialog.selectFile(file_name)

        dialog.setNameFilters(filters)
        if selected_filter is not None:
            dialog.selectNameFilter(selected_filter)

        if not dialog.exec_():
            raise OutputDeviceError.UserCanceledError()

        save_path = dialog.directory().absolutePath()
        Application.getInstance().getPreferences().setValue("local_file/dialog_save_path", save_path)

        selected_type = file_types[filters.index(dialog.selectedNameFilter())]
        Application.getInstance().getPreferences().setValue("local_file/last_used_type", selected_type["mime_type"])

        # Get file name from file dialog
        file_name = dialog.selectedFiles()[0]
        Logger.log("d", "Writing to [%s]..." % file_name)

        if os.path.exists(file_name):
            result = QMessageBox.question(None, catalog.i18nc("@title:window", "File Already Exists"), catalog.i18nc("@label Don't translate the XML tag <filename>!", "The file <filename>{0}</filename> already exists. Are you sure you want to overwrite it?").format(file_name))
            if result == QMessageBox.No:
                raise OutputDeviceError.UserCanceledError()

        self.writeStarted.emit(self)

        # Actually writing file
        if file_handler:
            file_writer = file_handler.getWriter(selected_type["id"])
        else:
            file_writer = Application.getInstance().getMeshFileHandler().getWriter(selected_type["id"])

        try:
            mode = selected_type["mode"]
            if mode == MeshWriter.OutputMode.TextMode:
                Logger.log("d", "Writing to Local File %s in text mode", file_name)
                stream = open(file_name, "wt", encoding = "utf-8")
            elif mode == MeshWriter.OutputMode.BinaryMode:
                Logger.log("d", "Writing to Local File %s in binary mode", file_name)
                stream = open(file_name, "wb")
            else:
                Logger.log("e", "Unrecognised OutputMode.")
                return None

            job = WriteFileJob(file_writer, stream, nodes, mode)
            job.setFileName(file_name)
            job.setAddToRecentFiles(True)  # The file will be added into the "recent files" list upon success
            job.progress.connect(self._onJobProgress)
            job.finished.connect(self._onWriteJobFinished)

            message = Message(catalog.i18nc("@info:progress Don't translate the XML tags <filename>!", "Saving to <filename>{0}</filename>").format(file_name),
                              0, False, -1 , catalog.i18nc("@info:title", "Saving"))
            message.show()

            job.setMessage(message)
            self._writing = True
            job.start()
        except PermissionError as e:
            Logger.log("e", "Permission denied when trying to write to %s: %s", file_name, str(e))
            raise OutputDeviceError.PermissionDeniedError(catalog.i18nc("@info:status Don't translate the XML tags <filename>!", "Permission denied when trying to save <filename>{0}</filename>").format(file_name)) from e
        except OSError as e:
            Logger.log("e", "Operating system would not let us write to %s: %s", file_name, str(e))
            raise OutputDeviceError.WriteRequestFailedError(catalog.i18nc("@info:status Don't translate the XML tags <filename> or <message>!", "Could not save to <filename>{0}</filename>: <message>{1}</message>").format(file_name, str(e))) from e

    def _onJobProgress(self, job, progress):
        self.writeProgress.emit(self, progress)

    def _onWriteJobFinished(self, job):
        self._writing = False
        self.writeFinished.emit(self)
        if job.getResult():
            self.writeSuccess.emit(self)
            message = Message(catalog.i18nc("@info:status Don't translate the XML tags <filename>!", "Saved to <filename>{0}</filename>").format(job.getFileName()), title = catalog.i18nc("@info:title", "File Saved"))
            message.addAction("open_folder", catalog.i18nc("@action:button", "Open Folder"), "open-folder", catalog.i18nc("@info:tooltip", "Open the folder containing the file"))
            message._folder = os.path.dirname(job.getFileName())
            message.actionTriggered.connect(self._onMessageActionTriggered)
            message.show()
        else:
            message = Message(catalog.i18nc("@info:status Don't translate the XML tags <filename> or <message>!", "Could not save to <filename>{0}</filename>: <message>{1}</message>").format(job.getFileName(), str(job.getError())), lifetime = 0, title = catalog.i18nc("@info:title", "Warning"))
            message.show()
            self.writeError.emit(self)

        try:
            job.getStream().close()
        except (OSError, PermissionError): #When you don't have the rights to do the final flush or the disk is full.
            message = Message(catalog.i18nc("@info:status", "Something went wrong saving to <filename>{0}</filename>: <message>{1}</message>").format(job.getFileName(), str(job.getError())), title = catalog.i18nc("@info:title", "Error"))
            message.show()
            self.writeError.emit(self)

    def _onMessageActionTriggered(self, message, action):
        if action == "open_folder" and hasattr(message, "_folder"):
            QDesktopServices.openUrl(QUrl.fromLocalFile(message._folder))
