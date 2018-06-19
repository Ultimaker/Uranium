# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import argparse
import os
import sys
import threading
from typing import Optional, TYPE_CHECKING

from UM.Controller import Controller
from UM.FileHandler.FileManager import FileManager
from UM.Logging.Logger import Logger
from UM.Mesh.MeshManager import MeshManager
from UM.Resources import Resources
import UM.Settings
import UM.Settings.ContainerStack
import UM.Settings.InstanceContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Preferences import Preferences
from UM.i18n import i18nCatalog

if TYPE_CHECKING:
    from UM.Backend.Backend import Backend


class Application:

    def __init__(self, name: str, version: str, build_type: str = "", is_debug_mode: bool = False,
                 *args, **kwargs) -> None:
        if Application.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        Application.__instance = self

        super().__init__()  # Call super to make multiple inheritance work.

        self._app_name = name  # type: str
        self._version = version  # type: str
        self._build_type = build_type  # type: str
        self._is_debug_mode = is_debug_mode  # type: bool
        self._use_external_backend = False  # type: bool

        self._cli_args = None  # type: argparse.Namespace
        self._cli_parser = argparse.ArgumentParser(prog = self._app_name,
                                                   add_help = False)  # type: argparse.ArgumentParser

        self._main_thread = threading.current_thread()  # type: threading.Thread

        self.default_theme = self._app_name  # type: str # Default theme is the application name
        self._default_language = "en_US"  # type: str

        self._preferences_filename = None  # type: str
        self._preferences = None  # type: Preferences

        self._container_registry_class = ContainerRegistry  # type: type
        self._container_registry = None  # type: ContainerRegistry

        self._file_manager = None  # type: FileManager
        self._mesh_manager = None  # type: MeshManager

        self._controller = None  # type: Controller
        self._backend = None  # type: Backend

        # Use default home directory
        self._app_home_dir = None  # type: Optional[str]
        self._app_install_dir = self.getInstallPrefix()  # type: str

    # Adds the command line options that can be parsed by the command line parser.
    # Can be overridden to add additional command line options to the parser.
    def addCommandLineOptions(self) -> None:
        self._cli_parser.add_argument("--version",
                                      action = "version",
                                      version = "%(prog)s version: {0}".format(self._version))
        self._cli_parser.add_argument("--external-backend",
                                      action = "store_true",
                                      default = False,
                                      help = "Use an externally started backend instead of starting it automatically. This is a debug feature to make it possible to run the engine with debug options enabled.")
        self._cli_parser.add_argument("--debug",
                                      action = "store_true",
                                      default = False,
                                      help = "Turn on the debug mode by setting this option.")

    def parseCliOptions(self) -> None:
        self._cli_args = self._cli_parser.parse_args()

        self._is_debug_mode = self._cli_args.debug or self._is_debug_mode
        self._use_external_backend = self._cli_args.external_backend

    # Performs initialization that must be done before start.
    def initialize(self) -> None:
        # For Ubuntu Unity this makes Qt use its own menu bar rather than pass it on to Unity.
        os.putenv("UBUNTU_MENUPROXY", "0")

        # Initialize Resources. Set the application name and version here because we can only know the actual info
        # after the __init__() has been called.
        Resources.ApplicationIdentifier = self._app_name
        Resources.ApplicationVersion = self._version
        Resources.HomeDir = self._app_home_dir

        Resources.addSearchPath(os.path.join(os.path.dirname(sys.executable), "resources"))
        Resources.addSearchPath(os.path.join(self._app_install_dir, "share", "uranium", "resources"))
        Resources.addSearchPath(os.path.join(self._app_install_dir, "Resources", "uranium", "resources"))
        Resources.addSearchPath(os.path.join(self._app_install_dir, "Resources", self._app_name, "resources"))

        if not hasattr(sys, "frozen"):
            Resources.addSearchPath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "resources"))

        i18nCatalog.setApplication(self)

        self._register_loggers()

        self._preferences = Preferences()
        self._preferences.addPreference("general/language", self._default_language)

        self._mesh_manager = MeshManager(self)

        self._file_manager = FileManager(self)
        from UM.MeshReaders.OBJReader import OBJReader
        from UM.MeshReaders.STLReader import STLReader
        self._file_manager.addReader(OBJReader(self))
        self._file_manager.addReader(STLReader(self))

        self._controller = Controller(self)

        Logger.log("i", "Initializing container registry ...")
        self._container_registry = self._container_registry_class(self)
        self._container_registry.initialize()

        UM.Settings.InstanceContainer.setContainerRegistry(self._container_registry)
        UM.Settings.ContainerStack.setContainerRegistry(self._container_registry)

    def _register_loggers(self) -> None:
        from UM.Logging.Logger import Logger
        from UM.Logging.ConsoleLogger import ConsoleLogger
        from UM.Logging.FileLogger import FileLogger

        Logger.addLogger(ConsoleLogger())
        Logger.addLogger(FileLogger(self._app_name + ".log"))

    def getApplicationName(self) -> str:
        return self._app_name

    def getVersion(self) -> str:
        return self._version

    def getBuildType(self) -> str:
        return self._build_type

    def getIsDebugMode(self) -> bool:
        return self._is_debug_mode

    def getUseExternalBackend(self) -> bool:
        return self._use_external_backend

    def getMeshManager(self) -> MeshManager:
        return self._mesh_manager

    def getFileManager(self) -> FileManager:
        return self._file_manager

    ##  Run the main event loop.
    #   This method should be re-implemented by subclasses to start the main event loop.
    #   \exception NotImplementedError
    def run(self):
        raise NotImplementedError("Run must be implemented by application")

    def getContainerRegistry(self):
        return self._container_registry

    ##  Get the preferences.
    #   \return preferences \type{Preferences}
    def getPreferences(self) -> Preferences:
        return self._preferences

    def savePreferences(self) -> None:
        if self._preferences_filename:
            self._preferences.writeToFile(self._preferences_filename)
        else:
            Logger.log("i", "Preferences filename not set. Unable to save file.")

    ##  Get the currently used IETF language tag.
    #   The returned tag is during runtime used to translate strings.
    #   \returns Language tag.
    def getApplicationLanguage(self) -> str:
        language = os.getenv("URANIUM_LANGUAGE")
        if not language:
            language = self._preferences.getValue("general/language")
        if not language:
            language = os.getenv("LANGUAGE")
        if not language:
            language = self._default_language

        return language

    def setBackend(self, backend: "Backend") -> None:
        self._backend = backend

    def getBackend(self) -> "Backend":
        return self._backend

    def getController(self) -> Controller:
        return self._controller

    @staticmethod
    def getInstallPrefix() -> str:
        if "python" in os.path.basename(sys.executable):
            return os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
        else:
            return os.path.abspath(os.path.join(os.path.dirname(sys.executable), ".."))

    __instance = None   # type: Application

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "Application":
        return cls.__instance
