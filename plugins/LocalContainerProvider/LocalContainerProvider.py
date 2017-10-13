# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Dict

from UM.Settings.ContainerProvider import ContainerProvider

class LocalContainerProvider(ContainerProvider):
    def loadContainer(self, container_id) -> "InstanceContainer":
        pass

    def loadMetadata(self) -> Dict[str, Dict[str, Any]]:
        pass