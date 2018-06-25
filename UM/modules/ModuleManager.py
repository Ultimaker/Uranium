from collections import OrderedDict
import importlib
import os
from typing import Dict, List, Optional, TYPE_CHECKING

from UM.Logging.Logger import Logger

if TYPE_CHECKING:
    from UM.Application import Application
    from .Module import Module


MODULE_INIT_FILE_NAME = "__init__.py"


class ModuleManager:

    def __init__(self, application: "Application") -> None:
        super().__init__()
        self._application = application  # type: Application

        self._module_search_paths = list()  # type: List[str]
        self._loaded_modules = {}  # type: Dict[str, Module]
        self._module_config = {}  # type: Dict[str, dict]

    def initialize(self) -> None:
        pass

    def addModule(self, module: "Module") -> None:
        if module.getName() in self._loaded_modules:
            Logger.log("e", "Module [%s] has already been added.", module.getName())
            return
        self._loaded_modules[module.getName()] = module
        Logger.log("i", "Module [%s] has been added.", module.getName())

    def addModuleSearchPath(self, path: str) -> None:
        path = os.path.abspath(path)
        if path not in self._module_search_paths:
            self._module_search_paths.append(path)
            Logger.log("d", "Module search path [%s] added.", path)

    # Finds and loads all modules. The initialization callbacks will be invoked later at each Application startup stage.
    def loadAllModules(self) -> None:
        for module_dir_path in self._getModuleDirPaths():
            module_import_name = module_dir_path.replace(os.pathsep, ".")
            imported_module = importlib.import_module(module_import_name, package = None)  # TODO: add package namespace?

            module = imported_module.get_module()
            self.addModule(module)

        self._loaded_modules = OrderedDict({k: v for k, v in sorted(self._loaded_modules.items())})

    def _getModuleDirPaths(self, paths: Optional[List[str]] = None):
        if not paths:
            paths = self._module_search_paths

        for folder in paths:
            if not os.path.isdir(folder):
                continue

            for _, dir_names, __ in os.walk(folder):
                for dir_name in dir_names:
                    dir_path = os.path.join(folder, dir_name)
                    module_file_path = os.path.join(dir_path, MODULE_INIT_FILE_NAME)
                    if os.path.isfile(module_file_path):
                        yield dir_path
                        continue
                    else:
                        self._getModuleDirPaths([dir_path])
                break

    def getLoadedPlugin(self, name: str) -> Optional["Module"]:
        return self._loaded_modules.get(name)

    #
    # Register functions
    #
    def registerMimeTypes(self) -> None:
        for name, module in self._loaded_modules.items():
            Logger.log("d", "Registering mime types for module [%s] ...", name)
            module.registerMimeTypes()

    def registerResources(self) -> None:
        for name, module in self._loaded_modules.items():
            Logger.log("d", "Registering resources for module [%s] ...", name)
            module.registerResources()

    def registerContainerTypes(self) -> None:
        for name, module in self._loaded_modules.items():
            Logger.log("d", "Registering container types for module [%s] ...", name)
            module.registerContainerTypes()

    def registerVersionUpgrades(self) -> None:
        for name, module in self._loaded_modules.items():
            Logger.log("d", "Registering version upgrade for module [%s] ...", name)
            module.registerContainerTypes()

    def registerBackends(self) -> None:
        for name, module in self._loaded_modules.items():
            Logger.log("d", "Registering backends for module [%s] ...", name)
            module.registerBackends()

    def registerApplicationTasks(self) -> None:
        for name, module in self._loaded_modules.items():
            Logger.log("d", "Registering backends for module [%s] ...", name)
            module.registerApplicationTasks()


__all__ = ["ModuleManager"]
