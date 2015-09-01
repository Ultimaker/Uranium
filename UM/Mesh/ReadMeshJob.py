# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Job import Job
from UM.Application import Application
from UM.Message import Message
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector
import time
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

    def getFileName(self):
        return self._filename

    def run(self):
        loading_message = Message(i18n_catalog.i18nc("@info:status", "Loading <filename>{0}</filename>", self._filename), lifetime = 0, dismissable = False)
        loading_message.setProgress(-1)
        loading_message.show()

        try:
            node = self._handler.read(self._filename)
        except Exception as e:
            print(e)
        if not node:
            loading_message.hide()

            result_message = Message(i18n_catalog.i18nc("@info:status", "Failed to load <filename>{0}</filename>", self._filename))
            result_message.show()
            return

        # Scale down to maximum bounds size if that is available
        if hasattr(Application.getInstance().getController().getScene(), "_maximum_bounds"):
            max_bounds = Application.getInstance().getController().getScene()._maximum_bounds
            node._resetAABB()
            bounding_box = node.getBoundingBox()
            timeout_counter = 0
            #As the calculation of the bounding box is in a seperate thread it might be that it's not done yet.
            while bounding_box.width == 0 or bounding_box.height == 0 or bounding_box.depth == 0:
                bounding_box = node.getBoundingBox()
                time.sleep(0.1)
                timeout_counter += 1
                if timeout_counter > 10:
                    break
            if max_bounds.width < bounding_box.width or max_bounds.height < bounding_box.height or max_bounds.depth < bounding_box.depth:
                largest_dimension = max(bounding_box.width, bounding_box.height, bounding_box.depth)

                scale_factor = 1.0
                if largest_dimension == bounding_box.width:
                    scale_factor = max_bounds.width / bounding_box.width
                elif largest_dimension == bounding_box.height:
                    scale_factor = max_bounds.height / bounding_box.height
                else:
                    scale_factor = max_bounds.depth / bounding_box.depth

                scale_vector = Vector(scale_factor, scale_factor, scale_factor)
                scale_message = Message(i18n_catalog.i18nc("", "Auto scaled object to {0} % of original size", ("%.2f" % scale_factor)))

                try:
                    node.scale(scale_vector)
                    scale_message.show()
                except Exception as e:
                    print(e)

        self.setResult(node)

        loading_message.hide()
        result_message = Message(i18n_catalog.i18nc("@info:status", "Loaded <filename>{0}</filename>", self._filename))
        result_message.show()
