# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Job import Job
from UM.Application import Application
from UM.Message import Message
from UM.Math.Vector import Vector
from UM.Preferences import Preferences
from UM.Logger import Logger
from UM.Mesh.MeshReader import MeshReader

import time
import math

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
        self.setResult([])
        reader = self._handler.getReaderForFile(self._filename)
        if not reader:
            result_message = Message(i18n_catalog.i18nc("@info:status", "Cannot open file type <filename>{0}</filename>", self._filename), lifetime = 0)
            result_message.show()
            return

        # Give the plugin a chance to display a dialog before showing the loading UI
        pre_read_result = reader.preRead(self._filename)

        if pre_read_result != MeshReader.PreReadResult.accepted:
            if pre_read_result == MeshReader.PreReadResult.failed:
                result_message = Message(i18n_catalog.i18nc("@info:status", "Failed to load <filename>{0}</filename>", self._filename), lifetime = 0)
                result_message.show()
            return

        loading_message = Message(i18n_catalog.i18nc("@info:status", "Loading <filename>{0}</filename>", self._filename), lifetime = 0, dismissable = False)
        loading_message.setProgress(-1)
        loading_message.show()

        Job.yieldThread() # Yield to any other thread that might want to do something else.

        nodes = None
        try:
            begin_time = time.time()
            nodes = self._handler.readerRead(reader, self._filename)
            end_time = time.time()
            Logger.log("d", "Loading mesh took %s seconds", end_time - begin_time)
        except:
            Logger.logException("e", "Exception in mesh loader")
        if not nodes:
            loading_message.hide()

            result_message = Message(i18n_catalog.i18nc("@info:status", "Failed to load <filename>{0}</filename>", self._filename), lifetime = 0)
            result_message.show()
            return

        # Scale down to maximum bounds size if that is available
        if hasattr(Application.getInstance().getController().getScene(), "_maximum_bounds"):
            for node in nodes:
                max_bounds = Application.getInstance().getController().getScene()._maximum_bounds
                node._resetAABB()
                build_bounds = node.getBoundingBox()

                if Preferences.getInstance().getValue("mesh/scale_to_fit") == True or Preferences.getInstance().getValue("mesh/scale_tiny_meshes") == True:
                    scale_factor_width = max_bounds.width / build_bounds.width
                    scale_factor_height = max_bounds.height / build_bounds.height
                    scale_factor_depth = max_bounds.depth / build_bounds.depth
                    scale_factor = min(scale_factor_width, scale_factor_depth, scale_factor_height)
                    if Preferences.getInstance().getValue("mesh/scale_to_fit") == True and (scale_factor_width < 1 or scale_factor_height < 1 or scale_factor_depth < 1): # Use scale factor to scale large object down
                        # Ignore scaling on models which are less than 1.25 times bigger than the build volume
                        ignore_factor = 1.25
                        if 1 / scale_factor < ignore_factor:
                            Logger.log("i", "Ignoring auto-scaling, because %.3d < %.3d" % (1 / scale_factor, ignore_factor))
                            scale_factor = 1
                        pass
                    elif Preferences.getInstance().getValue("mesh/scale_tiny_meshes") == True and (scale_factor_width > 100 and scale_factor_height > 100 and scale_factor_depth > 100):
                        # Round scale factor to lower factor of 10 to scale tiny object up (eg convert m to mm units)
                        scale_factor = math.pow(10, math.floor(math.log(scale_factor) / math.log(10)))
                    else:
                        scale_factor = 1

                    if scale_factor != 1:
                        scale_vector = Vector(scale_factor, scale_factor, scale_factor)
                        display_scale_factor = scale_factor * 100

                        scale_message = Message(i18n_catalog.i18nc("@info:status", "Auto scaled object to {0}% of original size", ("%i" % display_scale_factor)))

                        try:
                            node.scale(scale_vector)
                            scale_message.show()
                        except Exception:
                            Logger.logException("e", "While auto-scaling an exception has been raised")
        self.setResult(nodes)

        loading_message.hide()
