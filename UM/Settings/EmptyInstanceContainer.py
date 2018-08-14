# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from typing import Optional, Any

from UM.Logger import Logger
from UM.Settings.InstanceContainer import InstanceContainer
from UM.Settings.Interfaces import ContainerInterface
from UM.Settings.PropertyEvaluationContext import PropertyEvaluationContext

class EmptyInstanceContainer(InstanceContainer):
    def isDirty(self) -> bool:
        return False

    def getProperty(self, key: str, property_name: str, context: Optional[PropertyEvaluationContext] = None) -> Any:
        return None

    def setProperty(self, key: str, property_name: str, property_value: Any, container: ContainerInterface = None, set_from_cache: bool = False) -> None:
        Logger.log("e", "Setting property %s of container %s which should remain empty", key, self.getName())
        return

    def getConfigurationType(self) -> str:
        return ""  # FIXME: not sure if this is correct

    def serialize(self, ignored_metadata_keys: Optional[set] = None) -> str:
        return "[general]\n version = " + str(InstanceContainer.Version) + "\n name = empty\n definition = fdmprinter\n"


empty_container = EmptyInstanceContainer("empty")
