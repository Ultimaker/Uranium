# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Any, Dict, Iterable, Optional

from UM.Logging.Logger import Logger
from UM.Settings.Interfaces import ContainerInterface


class ContainerProvider:

    def __init__(self, container_registry) -> None:
        super().__init__()

        self._container_registry = container_registry

        self._metadata = {}  # type: Dict[str, Dict[str, Any]]
        self._containers = {}  # type: Dict[str, ContainerInterface]

    def __getitem__(self, container_id: str) -> ContainerInterface:
        if container_id not in self._containers:
            try:
                self._containers[container_id] = self.loadContainer(container_id)
            except:
                Logger.logException("e", "Failed to load container %s", container_id)
                raise
        return self._containers[container_id]

    def addMetadata(self, metadata: Dict[str, Any]) -> None:
        if "id" not in metadata:
            raise ValueError("The specified metadata has no ID.")
        if metadata["id"] in self._metadata:
            raise KeyError("The specified metadata already exists.")
        self._metadata[metadata["id"]] = metadata

    def getMetadata(self, container_id: str) -> Optional[Dict[str, Any]]:
        if container_id not in self._metadata:
            metadata = self.loadMetadata(container_id)
            if metadata is None:
                Logger.log("e", "Failed to load metadata of container %s", container_id)
                return None
        return self._metadata[container_id]

    def metadata(self) -> Dict[str, Dict[str, Any]]:
        return self._metadata

    def getAllIds(self) -> Iterable[str]:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement getAllIds.".format(class_name = self.__class__.__name__))

    def isReadOnly(self, container_id: str) -> bool:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement isReadOnly.".format(class_name = self.__class__.__name__))

    def loadContainer(self, container_id: str) -> "ContainerInterface":
        raise NotImplementedError("The container provider {class_name} doesn't properly implement loadContainer.".format(class_name = self.__class__.__name__))

    def loadMetadata(self, container_id: str) -> Dict[str, Any]:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement loadMetadata.".format(class_name = self.__class__.__name__))

    def removeContainer(self, container_id: str) -> None:
        raise NotImplementedError("The container provider {class_name} doesn't properly implement removeContainer.".format(class_name = self.__class__.__name__))