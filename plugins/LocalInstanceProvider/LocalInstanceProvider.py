# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Dict, Iterable, Optional

from UM.Settings.ContainerProvider import ContainerProvider #The class we're implementing.

class LocalInstanceProvider(ContainerProvider):
    def getAllIds(self) -> Iterable[str]:
        pass #TODO

    def loadContainer(self, container_id: str) -> "ContainerInterface":
        pass #TODO

    def loadMetadata(self, container_id: str) -> Optional[Dict[str, Any]]:
        pass #TODO