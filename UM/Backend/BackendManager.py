from collections import OrderedDict
from typing import Dict, Optional, TYPE_CHECKING

from UM.Logging.Logger import Logger

if TYPE_CHECKING:
    from UM.Application import Application
    from .Backend import Backend


class BackendManager:

    def __init__(self, application: "Application") -> None:
        super().__init__()
        self._application = application  # type: Application

        self._default_backend = None  # type: Optional[Backend]
        self._backend_dict = {}  # type: Dict[str, Backend]
        self._use_external_backend = False  # type: bool

    def registerBackend(self, backend: "Backend", is_default: bool = False) -> None:
        if backend.name in self._backend_dict:
            Logger.log("e", "Backend [%s] has already been registered, cannot register again", backend.name)
            return
        self._backend_dict[backend.name] = backend
        self._backend_dict = OrderedDict({k: v for k, v in sorted(self._backend_dict.items())})

        if is_default:
            self._default_backend = backend
            Logger.log("i", "Default backend set to ")

    def setDefaultBackendName(self, name: str) -> None:
        backend = self._backend_dict.get(name)
        if backend is None:
            raise ValueError("Cannot set default backend to [%s], cannot find it." % name)

        self._default_backend = backend
        Logger.log("i", "Default backend changed to [%s]", name)

    def getDefaultBackend(self) -> Optional["Backend"]:
        return self._default_backend

    def getBackends(self) -> Dict[str, "Backend"]:
        return self._backend_dict

    def setUseExternalBackend(self, value: bool) -> None:
        self._use_external_backend = value
        Logger.log("i", "Use external backend set to [%s]", self._use_external_backend)

    def getUseExtrernalBackend(self) -> bool:
        return self._use_external_backend
