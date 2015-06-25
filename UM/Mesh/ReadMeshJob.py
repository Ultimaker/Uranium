# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Job import Job
from UM.Application import Application
from UM.Message import Message
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Matrix import Matrix

import os.path

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

##  A Job subclass that performs mesh loading.
#
#   The result of this Job is a MeshData object.
class ReadMeshJob(Job):
    def __init__(self, filename):
        super().__init__()
        self._filename = filename
        self._handler = Application.getInstance().getMeshFileHandler()
        self._device = Application.getInstance().getStorageDevice("LocalFileStorage")

    def getFileName(self):
        return self._filename

    def run(self):
        loading_message = Message(i18n_catalog.i18nc("Loading mesh message, {0} is file name", "Loading {0}").format(self._filename), lifetime = 0, dismissable = False)
        loading_message.setProgress(-1)
        loading_message.show()

        mesh = self._handler.read(self._filename, self._device)

        # Scale down to maximum bounds size if that is available
        if hasattr(Application.getInstance().getController().getScene(), "_maximum_bounds"):
            max_bounds = Application.getInstance().getController().getScene()._maximum_bounds
            bbox = mesh.getExtents()

            if max_bounds.width < bbox.width or max_bounds.height < bbox.height or max_bounds.depth < bbox.depth:
                largest_dimension = max(bbox.width, bbox.height, bbox.depth)

                scale_factor = 1.0
                if largest_dimension == bbox.width:
                    scale_factor = max_bounds.width / bbox.width
                elif largest_dimension == bbox.height:
                    scale_factor = max_bounds.height / bbox.height
                else:
                    scale_factor = max_bounds.depth / bbox.depth

                matrix = Matrix()
                matrix.setByScaleFactor(scale_factor)
                mesh = mesh.getTransformed(matrix)

        self.setResult(mesh)

        loading_message.hide()
        result_message = Message(i18n_catalog.i18nc("Finished loading mesh message, {0} is file name", "Loaded {0}").format(self._filename))
        result_message.show()
