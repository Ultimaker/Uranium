# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import threading
import argparse
import os
import sys

from UM.Controller import Controller
from UM.PluginRegistry import PluginRegistry
from UM.Mesh.MeshFileHandler import MeshFileHandler
from UM.Resources import Resources
from UM.Operations.OperationStack import OperationStack
from UM.Event import CallFunctionEvent
from UM.Signal import Signal, signalemitter
from UM.Logger import Logger
from UM.Preferences import Preferences
from UM.OutputDevice.OutputDeviceManager import OutputDeviceManager
from UM.i18n import i18nCatalog
from UM.Workspace.WorkspaceFileHandler import WorkspaceFileHandler

import UM.Settings

##  Central object responsible for running the main event loop and creating other central objects.
#
#   The Application object is a central object for accessing other important objects. It is also
#   responsible for starting the main event loop. It is passed on to plugins so it can be easily
#   used to access objects required for those plugins.
@signalemitter
class Application():
    ##  Init method
    #
    #   \param name \type{string} The name of the application.
    #   \param version \type{string} Version, formatted as major.minor.rev
    def __init__(self, name, version, buildtype = "", **kwargs):
        if Application._instance != None:
            raise ValueError("Duplicate singleton creation")

        # If the constructor is called and there is no instance, set the instance to self.
        # This is done because we can't make constructor private
        Application._instance = self

        self._application_name = name
        self._version = version
        self._buildtype = buildtype

        os.putenv("UBUNTU_MENUPROXY", "0")  # For Ubuntu Unity this makes Qt use its own menu bar rather than pass it on to Unity.

        Signal._app = self
        Resources.ApplicationIdentifier = name
        i18nCatalog.setApplication(self)

        Resources.addSearchPath(os.path.join(os.path.dirname(sys.executable), "resources"))
        Resources.addSearchPath(os.path.join(Application.getInstallPrefix(), "share", "uranium", "resources"))
        Resources.addSearchPath(os.path.join(Application.getInstallPrefix(), "Resources", "uranium", "resources"))
        Resources.addSearchPath(os.path.join(Application.getInstallPrefix(), "Resources", self.getApplicationName(), "resources"))
        if not hasattr(sys, "frozen"):
            Resources.addSearchPath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "resources"))

        self._main_thread = threading.current_thread()

        super().__init__()  # Call super to make multiple inheritance work.

        self._renderer = None

        PluginRegistry.addType("backend", self.setBackend)
        PluginRegistry.addType("logger", Logger.addLogger)
        PluginRegistry.addType("extension", self.addExtension)

        preferences = Preferences.getInstance()
        preferences.addPreference("general/language", "en")
        preferences.addPreference("general/visible_settings", "")

        try:
            preferences.readFromFile(Resources.getPath(Resources.Preferences, self._application_name + ".cfg"))
        except FileNotFoundError:
            pass

        self._controller = Controller(self)
        self._mesh_file_handler = MeshFileHandler.getInstance()
        self._mesh_file_handler.setApplication(self)
        self._workspace_file_handler = WorkspaceFileHandler.getInstance()
        self._workspace_file_handler.setApplication(self)
        self._extensions = []
        self._backend = None
        self._output_device_manager = OutputDeviceManager()

        self._required_plugins = []

        self._operation_stack = OperationStack()

        self._plugin_registry = PluginRegistry.getInstance()

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

        UM.Settings.ContainerRegistry.setApplication(self)

        self._parsed_command_line = None
        self.parseCommandLine()

        self._visible_messages = []
        self._message_lock = threading.Lock()
        self.showMessageSignal.connect(self.showMessage)
        self.hideMessageSignal.connect(self.hideMessage)

        self._global_container_stack = None


    ##  Emitted when the application window was closed and we need to shut down the application
    applicationShuttingDown = Signal()

    showMessageSignal = Signal()

    hideMessageSignal = Signal()

    globalContainerStackChanged = Signal()

    def setGlobalContainerStack(self, stack):
        self._global_container_stack = stack
        self.globalContainerStackChanged.emit()

    def getGlobalContainerStack(self):
        return self._global_container_stack

    def hideMessage(self, message):
        raise NotImplementedError

    def showMessage(self, message):
        raise NotImplementedError

    ##  Get the version of the application
    #   \returns version \type{string}
    def getVersion(self):
        return self._version

    ##  Get the buildtype of the application
    #   \returns version \type{string}
    def getBuildType(self):
        return self._buildtype

    ##  Add a message to the visible message list so it will be displayed.
    #   This should only be called by message object itself.
    #   To show a message, simply create it and call its .show() function.
    #   \param message \type{Message} message object
    #   \sa Message::show()
    #def showMessage(self, message):
    #    with self._message_lock:
    #        if message not in self._visible_messages:
    #            self._visible_messages.append(message)
    #            self.visibleMessageAdded.emit(message)

    visibleMessageAdded = Signal()

    ##  Remove a message from the visible message list so it will no longer be displayed.
    #   This should only be called by message object itself.
    #   in principle, this should only be called by the message itself (hide)
    #   \param message \type{Message} message object
    #   \sa Message::hide()
    #def hideMessage(self, message):
    #    with self._message_lock:
    #        if message in self._visible_messages:
    #            self._visible_messages.remove(message)
    #            self.visibleMessageRemoved.emit(message)

    ##  Hide message by ID (as provided by built-in id function)
    #   \param message_id \type{long}
    def hideMessageById(self, message_id):
        found_message = None
        with self._message_lock:
            for message in self._visible_messages:
                if id(message) == int(message_id):
                    found_message = message
        if found_message is not None:
            self.hideMessageSignal.emit(found_message)

    visibleMessageRemoved = Signal()

    ##  Get list of all visible messages
    #   \returns visible_messages \type{list}
    def getVisibleMessages(self):
        with self._message_lock:
            return self._visible_messages

    ##  Function that needs to be overridden by child classes with a list of plugin it needs.
    def _loadPlugins(self):
        pass

    def getCommandLineOption(self, name, default = None): #pylint: disable=bad-whitespace
        if not self._parsed_command_line:
            self.parseCommandLine()
            Logger.log("d", "Command line options: %s", str(self._parsed_command_line))

        return self._parsed_command_line.get(name, default)

    ##  Get name of the application.
    #   \returns application_name \type{string}
    def getApplicationName(self):
        return self._application_name

    ##  Set name of the application.
    #   \param application_name \type{string}
    def setApplicationName(self, application_name):
        self._application_name = application_name

    def getApplicationLanguage(self):
        override_lang = os.getenv("URANIUM_LANGUAGE")
        if override_lang:
            return override_lang

        preflang = Preferences.getInstance().getValue("general/language")
        if preflang:
            return preflang

        env_lang = os.getenv("LANGUAGE")
        if env_lang:
            return env_lang

        return "en"

    ##  Application has a list of plugins that it *must* have. If it does not have these, it cannot function.
    #   These plugins can not be disabled in any way.
    #   \returns required_plugins \type{list}
    def getRequiredPlugins(self):
        return self._required_plugins

    ##  Set the plugins that the application *must* have in order to function.
    #   \param plugin_names \type{list} List of strings with the names of the required plugins
    def setRequiredPlugins(self, plugin_names):
        self._required_plugins = plugin_names

    ##  Set the backend of the application (the program that does the heavy lifting).
    #   \param backend \type{Backend}
    def setBackend(self, backend):
        self._backend = backend

    ##  Get the backend of the application (the program that does the heavy lifting).
    #   \returns Backend \type{Backend}
    def getBackend(self):
        return self._backend

    ##  Get the PluginRegistry of this application.
    #   \returns PluginRegistry \type{PluginRegistry}
    def getPluginRegistry(self):
        return self._plugin_registry

    ##  Get the Controller of this application.
    #   \returns Controller \type{Controller}
    def getController(self):
        return self._controller

    ##  Get the MeshFileHandler of this application.
    #   \returns MeshFileHandler \type{MeshFileHandler}
    def getMeshFileHandler(self):
        return self._mesh_file_handler

    def getWorkspaceFileHandler(self):
        return self._workspace_file_handler

    def getOperationStack(self):
        return self._operation_stack

    def getOutputDeviceManager(self):
        return self._output_device_manager

    ##  Run the main event loop.
    #   This method should be re-implemented by subclasses to start the main event loop.
    #   \exception NotImplementedError
    def run(self):
        raise NotImplementedError("Run must be implemented by application")

    ##  Return an application-specific Renderer object.
    #   \exception NotImplementedError
    def getRenderer(self):
        raise NotImplementedError("getRenderer must be implemented by subclasses.")

    ##  Post a function event onto the event loop.
    #
    #   This takes a CallFunctionEvent object and puts it into the actual event loop.
    #   \exception NotImplementedError
    def functionEvent(self, event):
        raise NotImplementedError("functionEvent must be implemented by subclasses.")

    ##  Call a function the next time the event loop runs.
    #
    #   \param function The function to call.
    #   \param args The positional arguments to pass to the function.
    #   \param kwargs The keyword arguments to pass to the function.
    def callLater(self, function, *args, **kwargs):
        event = CallFunctionEvent(function, args, kwargs)
        self.functionEvent(event)

    ##  Get the application"s main thread.
    def getMainThread(self):
        return self._main_thread

    ##  Return the singleton instance of the application object
    @classmethod
    def getInstance(cls):
        # Note: Explicit use of class name to prevent issues with inheritance.
        if Application._instance is None:
            Application._instance = cls()

        return Application._instance

    def parseCommandLine(self):
        parser = argparse.ArgumentParser(prog = self.getApplicationName()) #pylint: disable=bad-whitespace
        parser.add_argument("--version", action="version", version="%(prog)s {0}".format(self.getVersion()))
        parser.add_argument("--external-backend",
                            dest="external-backend",
                            action="store_true", default=False,
                            help="Use an externally started backend instead of starting it automatically.")
        self.addCommandLineOptions(parser)

        self._parsed_command_line = vars(parser.parse_args())

    ##  Can be overridden to add additional command line options to the parser.
    #
    #   \param parser \type{argparse.ArgumentParser} The parser that will parse the command line.
    def addCommandLineOptions(self, parser):
        pass

    def addExtension(self, extension):
        self._extensions.append(extension)

    def getExtensions(self):
        return self._extensions

    @staticmethod
    def getInstallPrefix():
        if "python" in os.path.basename(sys.executable):
            return os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
        else:
            return os.path.abspath(os.path.join(os.path.dirname(sys.executable), ".."))

    _instance = None
