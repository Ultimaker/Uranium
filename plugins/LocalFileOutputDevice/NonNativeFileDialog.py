# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
import os

from PyQt5.QtWidgets import QFileDialog, QLineEdit

from UM.Platform import Platform


#
# HACK: This class tries to fix double file extensions problems on Mac OS X with the FileDialog.
#
class NonNativeFileDialog(QFileDialog):

    def __init__(self, *args):
        super().__init__(*args)

        self._previous_extension = ""
        # Only do this on OS X
        if Platform.isOSX():
            self.filterSelected.connect(self._onFilterChanged)

    def _onFilterChanged(self, selected_filter: str):
        if not self.selectedFiles():
            return

        filename = self.selectedFiles()[0]
        if not filename:
            return
        if os.path.isdir(filename):
            return

        # Get the selected extension
        # The filter string we get here is a MINE extension string which looks like below:
        #         - "Text File (*.txt)"
        #         - "JPG Files (*.jpg, *.jpeg)"
        # We extract the extension part to for processing double/multi-extension file names.
        extension = selected_filter.rsplit(" ", 1)[-1]
        extension = extension.strip("()")
        extension = extension[2:]  # Remove the "*."
        extension_parts = extension.split(".")

        # Save the previous extension so we know what to remove if the user change between file types
        previous_extension = self._previous_extension.rsplit(" ", 1)[-1]
        previous_extension = previous_extension.strip("()")
        previous_extension = previous_extension[2:]  # Remove the "*."
        previous_extension_parts = previous_extension.split(".")
        self._previous_extension = selected_filter

        # Get the file name editor
        line_editor = self.findChild(QLineEdit)

        base_filename = os.path.basename(filename)
        filename_parts = base_filename.split(".")
        if len(filename_parts) == 1:
            # No extension, add the selected extension to the end
            new_base_filename = base_filename + "." + extension
            new_filepath = filename[:-len(base_filename)] + new_base_filename
            self.selectFile(new_filepath)
            line_editor.setText(new_base_filename)
            self.update()
            return

        current_extension_parts = filename_parts[1:]
        new_filepath = filename
        new_base_filename = base_filename
        if current_extension_parts != extension_parts:
            remove_count = 0
            for part in reversed(current_extension_parts):
                if part not in extension_parts and part not in previous_extension_parts:
                    break
                remove_count += 1
            new_parts = filename_parts[:1] + current_extension_parts[:len(current_extension_parts) - remove_count]
            new_base_filename = ".".join(new_parts + extension_parts)
            new_filepath = filename[:len(filename) - len(base_filename)] + new_base_filename
        self.selectFile(new_filepath)
        line_editor.setText(new_base_filename)
        self.update()

    def selectNameFilter(self, p_str):
        super().selectNameFilter(p_str)
        self._previous_extension = p_str
