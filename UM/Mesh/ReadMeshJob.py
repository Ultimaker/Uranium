# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Job import Job
from UM.Application import Application
from UM.Message import Message
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector
from UM.Preferences import Preferences
from UM.Logger import Logger
from UM.Mesh.MeshReader import MeshReader

import time
import os.path
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

        node = None
        try:
            begin_time = time.time()
            node = self._handler.readerRead(reader, self._filename)
            end_time = time.time()
            Logger.log("d", "Loading mesh took %s seconds", end_time - begin_time)
        except:
            Logger.logException("e", "Exception in mesh loader")
        if not node:
            loading_message.hide()

            result_message = Message(i18n_catalog.i18nc("@info:status", "Failed to load <filename>{0}</filename>", self._filename), lifetime = 0)
            result_message.show()
            return
        if node.getMeshData():
            node.getMeshData().setFileName(self._filename)
        # Scale down to maximum bounds size if that is available
        if hasattr(Application.getInstance().getController().getScene(), "_maximum_bounds"):
            max_bounds = Application.getInstance().getController().getScene()._maximum_bounds

            mesh_data = node.getMeshData()
            if mesh_data:
                bounding_box = mesh_data.getExtents()

                if Preferences.getInstance().getValue("mesh/scale_to_fit") == True or Preferences.getInstance().getValue("mesh/scale_tiny_meshes") == True:
                    scale_factor_width = max_bounds.width / bounding_box.width
                    scale_factor_height = max_bounds.height / bounding_box.height
                    scale_factor_depth = max_bounds.depth / bounding_box.depth
                    scale_factor = min(scale_factor_width,scale_factor_height,scale_factor_depth)
                    if Preferences.getInstance().getValue("mesh/scale_to_fit") == True and (scale_factor_width < 1 or scale_factor_height < 1 or scale_factor_depth < 1):
                        # Use scale factor to scale large object down
                        pass
                    elif Preferences.getInstance().getValue("mesh/scale_tiny_meshes") == True and (scale_factor_width > 100 and scale_factor_height > 100 and scale_factor_depth > 100):
                        # Round scale factor to lower factor of 10 to scale tiny object up (eg convert m to mm units)
                        scale_factor = math.pow(10, math.floor(math.log(scale_factor)/math.log(10)))
                    else:
                        scale_factor = 1

                    if scale_factor != 1:
                        scale_vector = Vector(scale_factor, scale_factor, scale_factor)
                        display_scale_factor = scale_factor * 100

                        scale_message = Message(i18n_catalog.i18nc("@info:status", "Auto scaled object to {0}% of original size", ("%i" % display_scale_factor)))

                        try:
                            node.scale(scale_vector)
                            scale_message.show()
                        except Exception as e:
                            print(e)
        self.setResult(node)

        loading_message.hide()
        #result_message = Message(i18n_catalog.i18nc("@info:status", "Loaded <filename>{0}</filename>", self._filename))
        #result_message.show()
