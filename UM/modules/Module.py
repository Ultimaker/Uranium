from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from UM.Application import Application


class Module:

    def __init__(self, name: str, application: "Application"):
        super().__init__()

        self._name = name  # type: str
        self._application = application  # type: Application
        self._enabled = True

    def getName(self) -> str:
        return self._name

    def setEnabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def getEnabled(self) -> bool:
        return self._enabled

    #
    # Registration callbacks
    #
    def registerMimeTypes(self) -> None:
        pass

    def registerResources(self) -> None:
        pass

    def registerContainerTypes(self) -> None:
        pass

    def registerVersionUpgrades(self) -> None:
        pass

    def registerBackends(self) -> None:
        pass

    def registerApplicationTasks(self) -> None:
        pass
