# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import threading
import argparse
import os
import sys

from UM.Controller import Controller
from UM.Message import Message #For typing.
from UM.PluginRegistry import PluginRegistry
from UM.Mesh.MeshFileHandler import MeshFileHandler
from UM.Resources import Resources
from UM.Operations.OperationStack import OperationStack
from UM.Event import CallFunctionEvent
from UM.Settings.ContainerRegistry import ContainerRegistry
import UM.Settings.ContainerStack
import UM.Settings.InstanceContainer
from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from UM.Preferences import Preferences
from UM.View.Renderer import Renderer #For typing.
from UM.OutputDevice.OutputDeviceManager import OutputDeviceManager
from UM.i18n import i18nCatalog
from UM.Workspace.WorkspaceFileHandler import WorkspaceFileHandler

import UM.Settings

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
    #   \param name The name of the application.
    #   \param version Version, formatted as major.minor.rev
    #   \param build_type Additional version info on the type of build this is,
    #   such as "master".
    #   \param is_debug_mode Whether to run in debug mode.
    #   \param parser The command line parser to use.
    def __init__(self, name: str, version: str, build_type: str = "", is_debug_mode: bool = False, parser: argparse.ArgumentParser = None, parsed_command_line: Dict[str, Any] = None, **kwargs) -> None:
        if Application._instance is not None:
            raise ValueError("Duplicate singleton creation")
        if parsed_command_line is None:
            parsed_command_line = {}

        # If the constructor is called and there is no instance, set the instance to self.
        # This is done because we can't make constructor private
        Application._instance = self

        self._application_name = name #type: str
        self._version = version #type: str
        self._build_type = build_type #type: str
        if "debug" in parsed_command_line.keys():
            if not parsed_command_line["debug"] and is_debug_mode:
                parsed_command_line["debug"] = is_debug_mode

        os.putenv("UBUNTU_MENUPROXY", "0")  # For Ubuntu Unity this makes Qt use its own menu bar rather than pass it on to Unity.

        Signal._app = self
        Signal._signalQueue = self
        Resources.ApplicationIdentifier = name
        Resources.ApplicationVersion = version

        Resources.addSearchPath(os.path.join(os.path.dirname(sys.executable), "resources"))
        Resources.addSearchPath(os.path.join(Application.getInstallPrefix(), "share", "uranium", "resources"))
        Resources.addSearchPath(os.path.join(Application.getInstallPrefix(), "Resources", "uranium", "resources"))
        Resources.addSearchPath(os.path.join(Application.getInstallPrefix(), "Resources", self.getApplicationName(), "resources"))

        if not hasattr(sys, "frozen"):
            Resources.addSearchPath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "resources"))

        self._main_thread = threading.current_thread() #type: threading.Thread

        super().__init__()  # Call super to make multiple inheritance work.
        i18nCatalog.setApplication(self)

        self._renderer = None #type: Renderer

        PluginRegistry.addType("backend", self.setBackend)
        PluginRegistry.addType("logger", Logger.addLogger)
        PluginRegistry.addType("extension", self.addExtension)

        self.default_theme = self.getApplicationName() #type: str

        preferences = Preferences.getInstance()
        preferences.addPreference("general/language", "en_US")
        preferences.addPreference("general/visible_settings", "")
        preferences.addPreference("general/plugins_to_remove", "")
        preferences.addPreference("general/disabled_plugins", "")

        try:
            preferences.readFromFile(Resources.getPath(Resources.Preferences, self._application_name + ".cfg"))
        except FileNotFoundError:
            pass

        self._controller = Controller(self) #type: Controller
        self._extensions = [] #type: List[Extension]
        self._backend = None #type: Backend
        self._output_device_manager = OutputDeviceManager() #type: OutputDeviceManager

        self._required_plugins = [] #type: List[str]

        self._operation_stack = OperationStack(self.getController()) #type: OperationStack

        self._plugin_registry = PluginRegistry.getInstance() #type: PluginRegistry

        self._plugin_registry.addPluginLocation(os.path.join(Application.getInstallPrefix(), "lib", "uranium"))
        self._plugin_registry.addPluginLocation(os.path.join(os.path.dirname(sys.executable), "plugins"))
        self._plugin_registry.addPluginLocation(os.path.join(Application.getInstallPrefix(), "Resources", "uranium", "plugins"))
        self._plugin_registry.addPluginLocation(os.path.join(Application.getInstallPrefix(), "Resources", self.getApplicationName(), "plugins"))
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

        self._plugin_registry.setApplication(self)

        ContainerRegistry.setApplication(self)
        UM.Settings.InstanceContainer.setContainerRegistry(self.getContainerRegistry())
        UM.Settings.ContainerStack.setContainerRegistry(self.getContainerRegistry())

        self._command_line_parser = parser #type: argparse.ArgumentParser
        self._parsed_command_line = parsed_command_line #type: Dict[str, Any]
        self.parseCommandLine()

        self._visible_messages = [] #type: List[Message]
        self._message_lock = threading.Lock() #type: threading.Lock
        self.showMessageSignal.connect(self.showMessage)
        self.hideMessageSignal.connect(self.hideMessage)

        self._global_container_stack = None #type: ContainerStack

    def getContainerRegistry(self) -> ContainerRegistry:
        return ContainerRegistry.getInstance()

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
    #   \returns version \type{string}
    def getVersion(self) -> str:
        return self._version

    @classmethod
    def getStaticVersion(cls) -> str:
        return "unknown"

    ##  Get the buildtype of the application
    #   \returns version \type{string}
    def getBuildType(self) -> str:
        return self._build_type

    def getIsDebugMode(self) -> bool:
        return self.getCommandLineOption("debug")

    visibleMessageAdded = Signal()

    ##  Hide message by ID (as provided by built-in id function)
    def hideMessageById(self, message_id: int):
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

    def getCommandLineOption(self, name: str, default: str = None) -> Any:
        if name not in self._parsed_command_line.keys():
            self.parseCommandLine()
            Logger.log("d", "Command line options: %s", str(self._parsed_command_line))

        return self._parsed_command_line.get(name, default)

    ##  Get name of the application.
    #   \returns application_name \type{string}
    def getApplicationName(self) -> str:
        return self._application_name

    ##  Get the preferences.
    #   \return preferences \type{Preferences}
    def getPreferences(self) -> Preferences:
        return Preferences.getInstance()

    ##  Get the currently used IETF language tag.
    #   The returned tag is during runtime used to translate strings.
    #   \returns Language tag.
    def getApplicationLanguage(self) -> str:
        override_lang = os.getenv("URANIUM_LANGUAGE")
        if override_lang:
            return override_lang

        preflang = Preferences.getInstance().getValue("general/language")
        if preflang:
            return preflang

        env_lang = os.getenv("LANGUAGE")
        if env_lang:
            return env_lang

        return "en_US"

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

    ##  Includes eg. last checks before entering the main event loop.
    def preRun(self) -> None:
        return None

    ##  Run the main event loop.
    #   This method should be re-implemented by subclasses to start the main event loop.
    #   \exception NotImplementedError
    def run(self) -> None:
        raise NotImplementedError("Run must be implemented by application")

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

    ##  Return the singleton instance of the application object
    @classmethod
    def getInstance(cls, **kwargs) -> "Application":
        # Note: Explicit use of class name to prevent issues with inheritance.
        if not Application._instance:
            Application._instance = cls(**kwargs)

        return Application._instance

    def getCommandlineParser(self, with_help: bool = False) -> argparse.ArgumentParser:
        if not self._command_line_parser:
            self._command_line_parser = argparse.ArgumentParser(prog = self.getApplicationName(), add_help = with_help) #pylint: disable=bad-whitespace
            self.addCommandLineOptions(self._command_line_parser, parsed_command_line = self._parsed_command_line)
        return self._command_line_parser

    def parseCommandLine(self) -> None:
        parser = self.getCommandlineParser()
        new_parsed_args = vars(parser.parse_known_args()[0])
        new_parsed_args.update(self._parsed_command_line)
        self._parsed_command_line = new_parsed_args

    ##  Can be overridden to add additional command line options to the parser.
    #
    #   \param parser The parser that will parse the command line.
    @classmethod
    def addCommandLineOptions(cls, parser: argparse.ArgumentParser, parsed_command_line: Dict[str, str] = None) -> None:
        if parsed_command_line is None:
            parsed_command_line = {}

        parser.add_argument("--version",
                            action = "version",
                            version = "%(prog)s {0}".format(cls.getStaticVersion()))

        parser.add_argument("--external-backend",
                            dest = "external-backend",
                            action = "store_true",
                            default = False,
                            help = "Use an externally started backend instead of starting it automatically. This is a debug feature to make it possible to run the engine with debug options enabled.")

        parser.add_argument('--headless',
                            action = 'store_true',
                            default = False,
                            help = "Hides all GUI elements.")

        if "debug" not in parsed_command_line.keys():
            parser.add_argument("--debug",
                                action = "store_true",
                                default = False,
                                help = "Turn on the debug mode by setting this option.")

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

    _instance = None    # type: Application
