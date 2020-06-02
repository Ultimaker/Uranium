# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM.Message import Message
from UM.Math.Vector import Vector
from UM.Logger import Logger

from UM.FileHandler.ReadFileJob import ReadFileJob

import math

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")


class ReadMeshJob(ReadFileJob):
    """A Job subclass that performs mesh loading.

    The result of this Job is a MeshData object.
    """

    def __init__(self, filename: str) -> None:
        super().__init__(filename)
        from UM.Qt.QtApplication import QtApplication
        self._application = QtApplication.getInstance()
        self._handler = QtApplication.getInstance().getMeshFileHandler()

    def run(self):
        super().run()

        if not self._result:
            self._result = []

        # Scale down to maximum bounds size if that is available
        if hasattr(self._application.getController().getScene(), "_maximum_bounds"):
            for node in self._result:
                max_bounds = self._application.getController().getScene()._maximum_bounds
                node._resetAABB()
                build_bounds = node.getBoundingBox()

                if build_bounds is None or max_bounds is None:
                    continue

                if self._application.getInstance().getPreferences().getValue("mesh/scale_to_fit") == True or self._application.getInstance().getPreferences().getValue("mesh/scale_tiny_meshes") == True:
                    scale_factor_width = max_bounds.width / build_bounds.width
                    scale_factor_height = max_bounds.height / build_bounds.height
                    scale_factor_depth = max_bounds.depth / build_bounds.depth
                    scale_factor = min(scale_factor_width, scale_factor_depth, scale_factor_height)
                    if self._application.getInstance().getPreferences().getValue("mesh/scale_to_fit") == True and (scale_factor_width < 1 or scale_factor_height < 1 or scale_factor_depth < 1): # Use scale factor to scale large object down
                        # Ignore scaling on models which are less than 1.25 times bigger than the build volume
                        ignore_factor = 1.25
                        if 1 / scale_factor < ignore_factor:
                            Logger.log("i", "Ignoring auto-scaling, because %.3d < %.3d" % (1 / scale_factor, ignore_factor))
                            scale_factor = 1
                        pass
                    elif self._application.getInstance().getPreferences().getValue("mesh/scale_tiny_meshes") == True and (scale_factor_width > 100 and scale_factor_height > 100 and scale_factor_depth > 100):
                        # Round scale factor to lower factor of 10 to scale tiny object up (eg convert m to mm units)
                        try:
                            scale_factor = math.pow(10, math.floor(math.log(scale_factor) / math.log(10)))
                        except:
                            # In certain cases the scale_factor can be inf which can make this fail. Just use 1 instead.
                            scale_factor = 1
                    else:
                        scale_factor = 1

                    if scale_factor != 1:
                        scale_vector = Vector(scale_factor, scale_factor, scale_factor)
                        display_scale_factor = scale_factor * 100

                        scale_message = Message(i18n_catalog.i18nc("@info:status", "Auto scaled object to {0}% of original size", ("%i" % display_scale_factor)), title = i18n_catalog.i18nc("@info:title", "Scaling Object"))

                        try:
                            node.scale(scale_vector)
                            scale_message.show()
                        except Exception:
                            Logger.logException("e", "While auto-scaling an exception has been raised")
