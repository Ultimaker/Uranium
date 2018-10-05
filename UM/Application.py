# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import argparse
import os
import sys
import threading

from UM.Controller import Controller
from UM.Message import Message #For typing.
from UM.PackageManager import PackageManager
from UM.PluginRegistry import PluginRegistry
from UM.Resources import Resources
from UM.Operations.OperationStack import OperationStack
from UM.Event import CallFunctionEvent
import UM.Settings
import UM.Settings.ContainerStack
import UM.Settings.InstanceContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from UM.Preferences import Preferences
from UM.View.Renderer import Renderer #For typing.
from UM.OutputDevice.OutputDeviceManager import OutputDeviceManager
from UM.i18n import i18nCatalog

try:
    from UM.LibraryDir import UraniumLibraryDir
except ImportError:
    UraniumLibraryDir = "lib"

from typing import TYPE_CHECKING, Dict, List, Callable, Any, Optional
if TYPE_CHECKING:
    from UM.Backend.Backend import Backend
    from UM.Settings.ContainerStack import ContainerStack
    from UM.Extension import Extension


##  Central object responsible for running the main event loop and creating other central objects.
#
#   The Application object is a central object for accessing other important objects. It is also
#   responsible for starting the main event loop. It is passed on to plugins so it can be easily
#   used to access objects required for those plugins.
@signalemitter
class Application:
    ##  Init method
    #
    #   \param name \type{string} The name of the application.
    #   \param version \type{string} Version, formatted as major.minor.rev
    #   \param build_type Additional version info on the type of build this is, such as "master".
    #   \param is_debug_mode Whether to run in debug mode.
    def __init__(self, name: str, version: str, build_type: str = "", is_debug_mode: bool = False, **kwargs) -> None:
        if Application.__instance is not None:
            raise RuntimeError("Try to create singleton '%s' more than once" % self.__class__.__name__)
        Application.__instance = self

        super().__init__()  # Call super to make multiple inheritance work.

        self._app_name = name #type: str
        self._version = version #type: str
        self._build_type = build_type #type: str
        self._is_debug_mode = is_debug_mode #type: bool
        self._is_headless = False #type: bool
        self._use_external_backend = False #type: bool

        self.CONFIG_LOCK_FILENAME = "{name}.lock".format(name = self._app_name) # type: str

        self._cli_args = None #type: argparse.Namespace
        self._cli_parser = argparse.ArgumentParser(prog = self._app_name, add_help = False) #type: argparse.ArgumentParser

        self._main_thread = threading.current_thread() #type: threading.Thread

        self.default_theme = self._app_name  #type: str # Default theme is the application name
        self._default_language = "en_US" #type: str

        self._preferences_filename = None #type: str
        self._preferences = None #type: Preferences

        self._extensions = [] #type: List[Extension]
        self._required_plugins = [] #type: List[str]

        self._package_manager_class = PackageManager  # type: type
        self._package_manager = None  # type: PackageManager

        self._plugin_registry = None #type: PluginRegistry
        self._container_registry_class = ContainerRegistry #type: type
        self._container_registry = None #type: ContainerRegistry
        self._global_container_stack = None #type: ContainerStack

        self._controller = None #type: Controller
        self._backend = None #type: Backend
        self._output_device_manager = None #type: OutputDeviceManager
        self._operation_stack = None #type: OperationStack

        self._visible_messages = [] #type: List[Message]
        self._message_lock = threading.Lock() #type: threading.Lock

        self._app_install_dir = self.getInstallPrefix() #type: str

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
        self._cli_parser.add_argument('--headless',
                                      action = 'store_true',
                                      default = False,
                                      help = "Hides all GUI elements.")
        self._cli_parser.add_argument("--debug",
                                      action = "store_true",
                                      default = False,
                                      help = "Turn on the debug mode by setting this option.")

    def parseCliOptions(self) -> None:
        self._cli_args = self._cli_parser.parse_args()

        self._is_headless = self._cli_args.headless
        self._is_debug_mode = self._cli_args.debug or self._is_debug_mode
        self._use_external_backend = self._cli_args.external_backend

    # Performs initialization that must be done before start.
    def initialize(self) -> None:
        # For Ubuntu Unity this makes Qt use its own menu bar rather than pass it on to Unity.
        os.putenv("UBUNTU_MENUPROXY", "0")

        # Custom signal handling
        Signal._app = self
        Signal._signalQueue = self

        # Initialize Resources. Set the application name and version here because we can only know the actual info
        # after the __init__() has been called.
        Resources.ApplicationIdentifier = self._app_name
        Resources.ApplicationVersion = self._version

        Resources.addSearchPath(os.path.join(os.path.dirname(sys.executable), "resources"))
        Resources.addSearchPath(os.path.join(self._app_install_dir, "share", "uranium", "resources"))
        Resources.addSearchPath(os.path.join(self._app_install_dir, "Resources", "uranium", "resources"))
        Resources.addSearchPath(os.path.join(self._app_install_dir, "Resources", self._app_name, "resources"))

        if not hasattr(sys, "frozen"):
            Resources.addSearchPath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "resources"))

        i18nCatalog.setApplication(self)

        PluginRegistry.addType("backend", self.setBackend)
        PluginRegistry.addType("logger", Logger.addLogger)
        PluginRegistry.addType("extension", self.addExtension)

        self._preferences = Preferences()
        self._preferences.addPreference("general/language", self._default_language)
        self._preferences.addPreference("general/visible_settings", "")
        self._preferences.addPreference("general/plugins_to_remove", "")
        self._preferences.addPreference("general/disabled_plugins", "")

        self._controller = Controller(self)
        self._output_device_manager = OutputDeviceManager()

        self._operation_stack = OperationStack(self._controller) # type: OperationStack

        self._plugin_registry = PluginRegistry(self)  #type: PluginRegistry

        self._plugin_registry.addPluginLocation(os.path.join(self._app_install_dir, UraniumLibraryDir, "uranium"))
        self._plugin_registry.addPluginLocation(os.path.join(os.path.dirname(sys.executable), "plugins"))
        self._plugin_registry.addPluginLocation(os.path.join(self._app_install_dir, "Resources", "uranium", "plugins"))
        self._plugin_registry.addPluginLocation(os.path.join(self._app_install_dir, "Resources", self._app_name, "plugins"))
        # Locally installed plugins
        local_path = os.path.join(Resources.getStoragePath(Resources.Resources), "plugins")
        # Ensure the local plugins directory exists
        try:
            os.makedirs(local_path)
        except OSError:
            pass
        self._plugin_registry.addPluginLocation(local_path)

        if not hasattr(sys, "frozen"):
            self._plugin_registry.addPluginLocation(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "plugins"))

        self._container_registry = self._container_registry_class(self)

        UM.Settings.InstanceContainer.setContainerRegistry(self._container_registry)
        UM.Settings.ContainerStack.setContainerRegistry(self._container_registry)

        # Initialize the package manager to remove and install scheduled packages.
        self._package_manager = self._package_manager_class(self)

        self.showMessageSignal.connect(self.showMessage)
        self.hideMessageSignal.connect(self.hideMessage)

        self.change_log_url = "https://github.com/Ultimaker/Uranium" #Where to find a more detailed description of the recent updates.

    def startSplashWindowPhase(self) -> None:
        pass

    def startPostSplashWindowPhase(self) -> None:
        pass

    ##  Run the main event loop.
    #   This method should be re-implemented by subclasses to start the main event loop.
    #   \exception NotImplementedError
    def run(self):
        self.addCommandLineOptions()
        self.parseCliOptions()
        self.initialize()

        self.startSplashWindowPhase()
        self.startPostSplashWindowPhase()

    def getContainerRegistry(self):
        return self._container_registry

    ##  Get the lock filename
    def getApplicationLockFilename(self) -> str:
        return self.CONFIG_LOCK_FILENAME

    ##  Emitted when the application window was closed and we need to shut down the application
    applicationShuttingDown = Signal()

    showMessageSignal = Signal()

    hideMessageSignal = Signal()

    globalContainerStackChanged = Signal()

    workspaceLoaded = Signal()

    def setGlobalContainerStack(self, stack: "ContainerStack") -> None:
        self._global_container_stack = stack
        self.globalContainerStackChanged.emit()

    def getGlobalContainerStack(self) -> Optional["ContainerStack"]:
        return self._global_container_stack

    def hideMessage(self, message: Message) -> None:
        raise NotImplementedError

    def showMessage(self, message: Message) -> None:
        raise NotImplementedError

    def showToastMessage(self, title: str, message: str) -> None:
        raise NotImplementedError

    ##  Get the version of the application
    def getVersion(self) -> str:
        return self._version

    ##  Get the build type of the application
    def getBuildType(self) -> str:
        return self._build_type

    def getIsDebugMode(self) -> bool:
        return self._is_debug_mode

    def getIsHeadLess(self) -> bool:
        return self._is_headless

    def getUseExternalBackend(self) -> bool:
        return self._use_external_backend

    visibleMessageAdded = Signal()

    ##  Hide message by ID (as provided by built-in id function)
    def hideMessageById(self, message_id: int) -> None:
        # If a user and the application tries to close same message dialog simultaneously, message_id could become an empty
        # string, and then the application will raise an error when trying to do "int(message_id)".
        # So we check the message_id here.
        if not message_id:
            return

        found_message = None
        with self._message_lock:
            for message in self._visible_messages:
                if id(message) == int(message_id):
                    found_message = message
        if found_message is not None:
            self.hideMessageSignal.emit(found_message)

    visibleMessageRemoved = Signal()

    ##  Get list of all visible messages
    def getVisibleMessages(self) -> List[Message]:
        with self._message_lock:
            return self._visible_messages

    ##  Function that needs to be overridden by child classes with a list of plugins it needs.
    def _loadPlugins(self) -> None:
        pass

    ##  Get name of the application.
    #   \returns app_name \type{string}
    def getApplicationName(self) -> str:
        return self._app_name

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

    ##  Application has a list of plugins that it *must* have. If it does not have these, it cannot function.
    #   These plugins can not be disabled in any way.
    def getRequiredPlugins(self) -> List[str]:
        return self._required_plugins

    ##  Set the plugins that the application *must* have in order to function.
    #   \param plugin_names \type{list} List of strings with the names of the required plugins
    def setRequiredPlugins(self, plugin_names: List[str]) -> None:
        self._required_plugins = plugin_names

    ##  Set the backend of the application (the program that does the heavy lifting).
    def setBackend(self, backend: "Backend") -> None:
        self._backend = backend

    ##  Get the backend of the application (the program that does the heavy lifting).
    #   \returns Backend \type{Backend}
    def getBackend(self) -> "Backend":
        return self._backend

    ##  Get the PluginRegistry of this application.
    #   \returns PluginRegistry \type{PluginRegistry}
    def getPluginRegistry(self) -> PluginRegistry:
        return self._plugin_registry

    ##  Get the Controller of this application.
    #   \returns Controller \type{Controller}
    def getController(self) -> Controller:
        return self._controller

    def getOperationStack(self) -> OperationStack:
        return self._operation_stack

    def getOutputDeviceManager(self) -> OutputDeviceManager:
        return self._output_device_manager

    ##  Return an application-specific Renderer object.
    #   \exception NotImplementedError
    def getRenderer(self) -> Renderer:
        raise NotImplementedError("getRenderer must be implemented by subclasses.")

    ##  Post a function event onto the event loop.
    #
    #   This takes a CallFunctionEvent object and puts it into the actual event loop.
    #   \exception NotImplementedError
    def functionEvent(self, event: CallFunctionEvent) -> None:
        raise NotImplementedError("functionEvent must be implemented by subclasses.")

    ##  Call a function the next time the event loop runs.
    #
    #   You can't get the result of this function directly. It won't block.
    #   \param function The function to call.
    #   \param args The positional arguments to pass to the function.
    #   \param kwargs The keyword arguments to pass to the function.
    def callLater(self, func: Callable[..., Any], *args, **kwargs) -> None:
        event = CallFunctionEvent(func, args, kwargs)
        self.functionEvent(event)

    ##  Get the application's main thread.
    def getMainThread(self) -> threading.Thread:
        return self._main_thread

    def addExtension(self, extension: "Extension") -> None:
        self._extensions.append(extension)

    def getExtensions(self) -> List["Extension"]:
        return self._extensions

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
