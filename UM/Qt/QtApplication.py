# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import sys
import os
import signal
from typing import List
from typing import Any, cast, Dict, Optional

from PyQt5.QtCore import Qt, QCoreApplication, QEvent, QUrl, pyqtProperty, pyqtSignal, QT_VERSION_STR, PYQT_VERSION_STR
from UM.FlameProfiler import pyqtSlot
from PyQt5.QtQml import QQmlApplicationEngine, QQmlComponent, QQmlContext, QQmlError
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox, QSystemTrayIcon
from PyQt5.QtGui import QIcon, QPixmap, QFontMetrics, QSurfaceFormat
from PyQt5.QtCore import QTimer

from UM.Backend.Backend import Backend #For typing.
from UM.ConfigurationErrorMessage import ConfigurationErrorMessage
from UM.FileHandler.ReadFileJob import ReadFileJob
from UM.FileHandler.WriteFileJob import WriteFileJob
from UM.Mesh.MeshFileHandler import MeshFileHandler
from UM.Qt.Bindings.Theme import Theme
from UM.Workspace.WorkspaceFileHandler import WorkspaceFileHandler
from UM.Application import Application
from UM.PackageManager import PackageManager #For typing.
from UM.Qt.QtRenderer import QtRenderer
from UM.Qt.Bindings.Bindings import Bindings
from UM.Qt.Bindings.MainWindow import MainWindow #For typing.
from UM.Signal import Signal, signalemitter
from UM.Resources import Resources
from UM.Logger import Logger
from UM.Message import Message #For typing.
from UM.i18n import i18nCatalog
from UM.Job import Job #For typing.
from UM.JobQueue import JobQueue
from UM.VersionUpgradeManager import VersionUpgradeManager
from UM.View.GL.OpenGLContext import OpenGLContext
from UM.Version import Version

from UM.TaskManagement.HttpRequestManager import HttpRequestManager

from UM.Operations.GroupedOperation import GroupedOperation #To clear the scene.
from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation #To clear the scene.
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator #To clear the scene.
from UM.Scene.SceneNode import SceneNode #To clear the scene.
from UM.Scene.Selection import Selection #To clear the selection after clearing the scene.

import UM.Settings.InstanceContainer  # For version upgrade to know the version number.
import UM.Settings.ContainerStack  # For version upgrade to know the version number.
import UM.Preferences  # For version upgrade to know the version number.
from UM.Mesh.ReadMeshJob import ReadMeshJob

import UM.Qt.Bindings.Theme
from UM.PluginRegistry import PluginRegistry
from PyQt5.QtCore import QObject


# Raised when we try to use an unsupported version of a dependency.
class UnsupportedVersionError(Exception):
    pass


# Check PyQt version, we only support 5.9 or higher.
major, minor = PYQT_VERSION_STR.split(".")[0:2]
if int(major) < 5 or (int(major) == 5 and int(minor) < 9):
    raise UnsupportedVersionError("This application requires at least PyQt 5.9.0")


@signalemitter
class QtApplication(QApplication, Application):
    """Application subclass that provides a Qt application object."""

    pluginsLoaded = Signal()
    applicationRunning = Signal()

    def __init__(self, tray_icon_name: str = None, **kwargs) -> None:
        plugin_path = ""
        if sys.platform == "win32":
            if hasattr(sys, "frozen"):
                plugin_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "PyQt5", "plugins")
                Logger.log("i", "Adding QT5 plugin path: %s", plugin_path)
                QCoreApplication.addLibraryPath(plugin_path)
            else:
                import site
                for sitepackage_dir in site.getsitepackages():
                    QCoreApplication.addLibraryPath(os.path.join(sitepackage_dir, "PyQt5", "plugins"))
        elif sys.platform == "darwin":
            plugin_path = os.path.join(self.getInstallPrefix(), "Resources", "plugins")

        if plugin_path:
            Logger.log("i", "Adding QT5 plugin path: %s", plugin_path)
            QCoreApplication.addLibraryPath(plugin_path)

        # use Qt Quick Scene Graph "basic" render loop
        os.environ["QSG_RENDER_LOOP"] = "basic"

        super().__init__(sys.argv, **kwargs) # type: ignore

        self._qml_import_paths = [] #type: List[str]
        self._main_qml = "main.qml" #type: str
        self._qml_engine = None #type: Optional[QQmlApplicationEngine]
        self._main_window = None #type: Optional[MainWindow]
        self._tray_icon_name = tray_icon_name #type: Optional[str]
        self._tray_icon = None #type: Optional[str]
        self._tray_icon_widget = None #type: Optional[QSystemTrayIcon]
        self._theme = None #type: Optional[Theme]
        self._renderer = None #type: Optional[QtRenderer]

        self._job_queue = None #type: Optional[JobQueue]
        self._version_upgrade_manager = None #type: Optional[VersionUpgradeManager]

        self._is_shutting_down = False #type: bool

        self._recent_files = [] #type: List[QUrl]

        self._configuration_error_message = None #type: Optional[ConfigurationErrorMessage]

        self._http_network_request_manager = HttpRequestManager(parent = self)

        #Metadata required for the file dialogues.
        self.setOrganizationDomain("https://ultimaker.com/")
        self.setOrganizationName("Ultimaker B.V.")

    def addCommandLineOptions(self) -> None:
        super().addCommandLineOptions()
        # This flag is used by QApplication. We don't process it.
        self._cli_parser.add_argument("-qmljsdebugger",
                                      help = "For Qt's QML debugger compatibility")

    def initialize(self) -> None:
        super().initialize()

        preferences = Application.getInstance().getPreferences()
        preferences.addPreference("view/force_empty_shader_cache", False)
        preferences.addPreference("view/opengl_version_detect", OpenGLContext.OpenGlVersionDetect.Autodetect)

        # Read preferences here (upgrade won't work) to get:
        #  - The language in use, so the splash window can be shown in the correct language.
        #  - The OpenGL 'force' parameters.
        try:
            preferences_filename = Resources.getPath(Resources.Preferences, self._app_name + ".cfg")
            self._preferences.readFromFile(preferences_filename)
        except FileNotFoundError:
            Logger.log("i", "Preferences file not found, ignore and use default language '%s'", self._default_language)

        # Initialize the package manager to remove and install scheduled packages.
        self._package_manager = self._package_manager_class(self, parent = self)

        self._mesh_file_handler = MeshFileHandler(self) #type: MeshFileHandler
        self._workspace_file_handler = WorkspaceFileHandler(self) #type: WorkspaceFileHandler

        # Remove this and you will get Windows 95 style for all widgets if you are using Qt 5.10+
        self.setStyle("fusion")

        if preferences.getValue("view/force_empty_shader_cache"):
            self.setAttribute(Qt.AA_DisableShaderDiskCache)
        self.setAttribute(Qt.AA_UseDesktopOpenGL)
        if preferences.getValue("view/opengl_version_detect") != OpenGLContext.OpenGlVersionDetect.ForceModern:
            major_version, minor_version, profile = OpenGLContext.detectBestOpenGLVersion(
                preferences.getValue("view/opengl_version_detect") == OpenGLContext.OpenGlVersionDetect.ForceLegacy)
        else:
            Logger.info("Force 'modern' OpenGL (4.1 core) -- overrides 'force legacy opengl' preference.")
            major_version, minor_version, profile = (4, 1, QSurfaceFormat.CoreProfile)

        if major_version is None or minor_version is None or profile is None:
            Logger.log("e", "Startup failed because OpenGL version probing has failed: tried to create a 2.0 and 4.1 context. Exiting")
            if not self.getIsHeadLess():
                QMessageBox.critical(None, "Failed to probe OpenGL",
                                     "Could not probe OpenGL. This program requires OpenGL 2.0 or higher. Please check your video card drivers.")
            sys.exit(1)
        else:
            opengl_version_str = OpenGLContext.versionAsText(major_version, minor_version, profile)
            Logger.log("d", "Detected most suitable OpenGL context version: %s", opengl_version_str)
        if not self.getIsHeadLess():
            OpenGLContext.setDefaultFormat(major_version, minor_version, profile = profile)

        self._qml_import_paths.append(os.path.join(os.path.dirname(sys.executable), "qml"))
        self._qml_import_paths.append(os.path.join(self.getInstallPrefix(), "Resources", "qml"))

        Logger.log("i", "Initializing job queue ...")
        self._job_queue = JobQueue()
        self._job_queue.jobFinished.connect(self._onJobFinished)

        Logger.log("i", "Initializing version upgrade manager ...")
        self._version_upgrade_manager = VersionUpgradeManager(self)

    def startSplashWindowPhase(self) -> None:
        super().startSplashWindowPhase()
        i18n_catalog = i18nCatalog("uranium")
        self.showSplashMessage(i18n_catalog.i18nc("@info:progress", "Initializing package manager..."))
        self._package_manager.initialize()

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # This is done here as a lot of plugins require a correct gl context. If you want to change the framework,
        # these checks need to be done in your <framework>Application.py class __init__().

        self._configuration_error_message = ConfigurationErrorMessage(self,
              i18n_catalog.i18nc("@info:status", "Your configuration seems to be corrupt."),
              lifetime = 0,
              title = i18n_catalog.i18nc("@info:title", "Configuration errors")
              )
        # Remove, install, and then loading plugins
        self.showSplashMessage(i18n_catalog.i18nc("@info:progress", "Loading plugins..."))
        # Remove and install the plugins that have been scheduled
        self._plugin_registry.initializeBeforePluginsAreLoaded()
        self._loadPlugins()
        self._plugin_registry.checkRequiredPlugins(self.getRequiredPlugins())
        self.pluginsLoaded.emit()

        self.showSplashMessage(i18n_catalog.i18nc("@info:progress", "Updating configuration..."))
        with self._container_registry.lockFile():
            VersionUpgradeManager.getInstance().upgrade()

        # Load preferences again because before we have loaded the plugins, we don't have the upgrade routine for
        # the preferences file. Now that we have, load the preferences file again so it can be upgraded and loaded.
        self.showSplashMessage(i18n_catalog.i18nc("@info:progress", "Loading preferences..."))
        try:
            preferences_filename = Resources.getPath(Resources.Preferences, self._app_name + ".cfg")
            with open(preferences_filename, "r", encoding = "utf-8") as f:
                serialized = f.read()
            # This performs the upgrade for Preferences
            self._preferences.deserialize(serialized)
            self._preferences.setValue("general/plugins_to_remove", "")
            self._preferences.writeToFile(preferences_filename)
        except (FileNotFoundError, UnicodeDecodeError):
            Logger.log("i", "The preferences file cannot be found or it is corrupted, so we will use default values")

        self.processEvents()
        # Force the configuration file to be written again since the list of plugins to remove maybe changed
        try:
            self._preferences_filename = Resources.getPath(Resources.Preferences, self._app_name + ".cfg")
            self._preferences.readFromFile(self._preferences_filename)
        except FileNotFoundError:
            Logger.log("i", "The preferences file '%s' cannot be found, will use default values",
                       self._preferences_filename)
            self._preferences_filename = Resources.getStoragePath(Resources.Preferences, self._app_name + ".cfg")

        # FIXME: This is done here because we now use "plugins.json" to manage plugins instead of the Preferences file,
        # but the PluginRegistry will still import data from the Preferences files if present, such as disabled plugins,
        # so we need to reset those values AFTER the Preferences file is loaded.
        self._plugin_registry.initializeAfterPluginsAreLoaded()

        # Check if we have just updated from an older version
        self._preferences.addPreference("general/last_run_version", "")
        last_run_version_str = self._preferences.getValue("general/last_run_version")
        if not last_run_version_str:
            last_run_version_str = self._version
        last_run_version = Version(last_run_version_str)
        current_version = Version(self._version)
        if last_run_version < current_version:
            self._just_updated_from_old_version = True
        self._preferences.setValue("general/last_run_version", str(current_version))
        self._preferences.writeToFile(self._preferences_filename)

        # Preferences: recent files
        self._preferences.addPreference("%s/recent_files" % self._app_name, "")
        file_names = self._preferences.getValue("%s/recent_files" % self._app_name).split(";")
        for file_name in file_names:
            if not os.path.isfile(file_name):
                continue
            self._recent_files.append(QUrl.fromLocalFile(file_name))

        if not self.getIsHeadLess():
            # Initialize System tray icon and make it invisible because it is used only to show pop up messages
            self._tray_icon = None
            if self._tray_icon_name:
                try:
                    self._tray_icon = QIcon(Resources.getPath(Resources.Images, self._tray_icon_name))
                    self._tray_icon_widget = QSystemTrayIcon(self._tray_icon)
                    self._tray_icon_widget.setVisible(False)
                except FileNotFoundError:
                    Logger.log("w", "Could not find the icon %s", self._tray_icon_name)

    def initializeEngine(self) -> None:
        # TODO: Document native/qml import trickery
        self._qml_engine = QQmlApplicationEngine(self)
        self.processEvents()
        self._qml_engine.setOutputWarningsToStandardError(False)
        self._qml_engine.warnings.connect(self.__onQmlWarning)

        for path in self._qml_import_paths:
            self._qml_engine.addImportPath(path)

        if not hasattr(sys, "frozen"):
            self._qml_engine.addImportPath(os.path.join(os.path.dirname(__file__), "qml"))

        self._qml_engine.rootContext().setContextProperty("QT_VERSION_STR", QT_VERSION_STR)
        self.processEvents()
        self._qml_engine.rootContext().setContextProperty("screenScaleFactor", self._screenScaleFactor())

        self.registerObjects(self._qml_engine)

        Bindings.register()

        # Preload theme. The theme will be loaded on first use, which will incur a ~0.1s freeze on the MainThread.
        # Do it here, while the splash screen is shown. Also makes this freeze explicit and traceable.
        self.getTheme()
        self.processEvents()

        i18n_catalog = i18nCatalog("uranium")
        self.showSplashMessage(i18n_catalog.i18nc("@info:progress", "Loading UI..."))
        self._qml_engine.load(self._main_qml)
        self.engineCreatedSignal.emit()

    recentFilesChanged = pyqtSignal()

    @pyqtProperty("QVariantList", notify=recentFilesChanged)
    def recentFiles(self) -> List[QUrl]:
        return self._recent_files

    def _onJobFinished(self, job: Job) -> None:
        if isinstance(job, WriteFileJob):
            if not job.getResult() or not job.getAddToRecentFiles():
                # For a write file job, if it failed or it doesn't need to be added to the recent files list, we do not
                # add it.
                return
        elif (not isinstance(job, ReadMeshJob) and not isinstance(job, ReadFileJob)) or not job.getResult():
            return

        if isinstance(job, (ReadMeshJob, ReadFileJob, WriteFileJob)):
            self.addFileToRecentFiles(job.getFileName())

    def addFileToRecentFiles(self, file_name: str) -> None:
        file_path = QUrl.fromLocalFile(file_name)

        if file_path in self._recent_files:
            self._recent_files.remove(file_path)

        self._recent_files.insert(0, file_path)
        if len(self._recent_files) > 10:
            del self._recent_files[10]

        pref = ""
        for path in self._recent_files:
            pref += path.toLocalFile() + ";"

        self.getPreferences().setValue("%s/recent_files" % self.getApplicationName(), pref)
        self.recentFilesChanged.emit()

    def run(self) -> None:
        super().run()

    def hideMessage(self, message: Message) -> None:
        with self._message_lock:
            if message in self._visible_messages:
                message.hide(send_signal = False)  # we're in handling hideMessageSignal so we don't want to resend it
                self._visible_messages.remove(message)
                self.visibleMessageRemoved.emit(message)

    def showMessage(self, message: Message) -> None:
        with self._message_lock:
            if message not in self._visible_messages:
                self._visible_messages.append(message)
                message.setLifetimeTimer(QTimer())
                message.setInactivityTimer(QTimer())
                self.visibleMessageAdded.emit(message)

        # also show toast message when the main window is minimized
        self.showToastMessage(self._app_name, message.getText())

    def _onMainWindowStateChanged(self, window_state: int) -> None:
        if self._tray_icon and self._tray_icon_widget:
            visible = window_state == Qt.WindowMinimized
            self._tray_icon_widget.setVisible(visible)

    # Show toast message using System tray widget.
    def showToastMessage(self, title: str, message: str) -> None:
        if self.checkWindowMinimizedState() and self._tray_icon_widget:
            # NOTE: Qt 5.8 don't support custom icon for the system tray messages, but Qt 5.9 does.
            #       We should use the custom icon when we switch to Qt 5.9
            self._tray_icon_widget.showMessage(title, message)

    def setMainQml(self, path: str) -> None:
        self._main_qml = path

    def exec_(self, *args: Any, **kwargs: Any) -> None:
        self.applicationRunning.emit()
        super().exec_(*args, **kwargs)

    @pyqtSlot()
    def reloadQML(self) -> None:
        # only reload when it is a release build
        if not self.getIsDebugMode():
            return
        if self._qml_engine and self._theme:
            self._qml_engine.clearComponentCache()
            self._theme.reload()
            self._qml_engine.load(self._main_qml)
            # Hide the window. For some reason we can't close it yet. This needs to be done in the onComponentCompleted.
            for obj in self._qml_engine.rootObjects():
                if obj != self._qml_engine.rootObjects()[-1]:
                    obj.hide()

    @pyqtSlot()
    def purgeWindows(self) -> None:
        # Close all root objects except the last one.
        # Should only be called by onComponentCompleted of the mainWindow.
        if self._qml_engine:
            for obj in self._qml_engine.rootObjects():
                if obj != self._qml_engine.rootObjects()[-1]:
                    obj.close()

    @pyqtSlot("QList<QQmlError>")
    def __onQmlWarning(self, warnings: List[QQmlError]) -> None:
        for warning in warnings:
            Logger.log("w", warning.toString())

    engineCreatedSignal = Signal()

    def isShuttingDown(self) -> bool:
        return self._is_shutting_down

    def registerObjects(self, engine) -> None: #type: ignore #Don't type engine, because the type depends on the platform you're running on so it always gives an error somewhere.
        engine.rootContext().setContextProperty("PluginRegistry", PluginRegistry.getInstance())

    def getRenderer(self) -> QtRenderer:
        if not self._renderer:
            self._renderer = QtRenderer()

        return cast(QtRenderer, self._renderer)

    mainWindowChanged = Signal()

    def getMainWindow(self) -> Optional[MainWindow]:
        return self._main_window

    def setMainWindow(self, window: MainWindow) -> None:
        if window != self._main_window:
            if self._main_window is not None:
                self._main_window.windowStateChanged.disconnect(self._onMainWindowStateChanged)

            self._main_window = window
            if self._main_window is not None:
                self._main_window.windowStateChanged.connect(self._onMainWindowStateChanged)
            self.mainWindowChanged.emit()

    def setVisible(self, visible: bool) -> None:
        if self._main_window is not None:
            self._main_window.visible = visible

    @property
    def isVisible(self) -> bool:
        if self._main_window is not None:
            return self._main_window.visible #type: ignore #MyPy doesn't realise that self._main_window cannot be None here.
        return False

    def getTheme(self) -> Optional[Theme]:
        if self._theme is None:
            if self._qml_engine is None:
                Logger.log("e", "The theme cannot be accessed before the engine is initialised")
                return None

            self._theme = UM.Qt.Bindings.Theme.Theme.getInstance(self._qml_engine)
        return self._theme

    #   Handle a function that should be called later.
    def functionEvent(self, event: QEvent) -> None:
        e = _QtFunctionEvent(event)
        QCoreApplication.postEvent(self, e)

    #   Handle Qt events
    def event(self, event: QEvent) -> bool:
        if event.type() == _QtFunctionEvent.QtFunctionEvent:
            event._function_event.call()
            return True

        return super().event(event)

    def windowClosed(self, save_data: bool = True) -> None:
        Logger.log("d", "Shutting down %s", self.getApplicationName())
        self._is_shutting_down = True

        # garbage collect tray icon so it gets properly closed before the application is closed
        self._tray_icon_widget = None

        if save_data:
            try:
                self.savePreferences()
            except Exception as e:
                Logger.log("e", "Exception while saving preferences: %s", repr(e))

        try:
            self.applicationShuttingDown.emit()
        except Exception as e:
            Logger.log("e", "Exception while emitting shutdown signal: %s", repr(e))

        try:
            self.getBackend().close()
        except Exception as e:
            Logger.log("e", "Exception while closing backend: %s", repr(e))

        if self._tray_icon_widget:
            self._tray_icon_widget.deleteLater()

        self.quit()

    def checkWindowMinimizedState(self) -> bool:
        if self._main_window is not None and self._main_window.windowState() == Qt.WindowMinimized:
            return True
        else:
            return False

    @pyqtSlot(result = "QObject*")
    def getBackend(self) -> Backend:
        """Get the backend of the application (the program that does the heavy lifting).

        The backend is also a QObject, which can be used from qml.
        """

        return self._backend

    @pyqtProperty("QVariant", constant = True)
    def backend(self) -> Backend:
        """Property used to expose the backend

        It is made static as the backend is not supposed to change during runtime.
        This makes the connection between backend and QML more reliable than the pyqtSlot above.
        :returns: Backend :type{Backend}
        """

        return self.getBackend()

    splash = None  # type: Optional[QSplashScreen]
    """Create a class variable so we can manage the splash in the CrashHandler dialog when the Application instance
    is not yet created, e.g. when an error occurs during the initialization
    """

    def createSplash(self) -> None:
        if not self.getIsHeadLess():
            try:
                QtApplication.splash = self._createSplashScreen()
            except FileNotFoundError:
                QtApplication.splash = None
            else:
                if QtApplication.splash:
                    QtApplication.splash.show()
                    self.processEvents()

    def showSplashMessage(self, message: str) -> None:
        """Display text on the splash screen."""

        if not QtApplication.splash:
            self.createSplash()

        if QtApplication.splash:
            self.processEvents()  # Process events from previous loading phase before updating the message
            QtApplication.splash.showMessage(message, Qt.AlignHCenter | Qt.AlignVCenter)  # Now update the message
            self.processEvents()  # And make sure it is immediately visible
        elif self.getIsHeadLess():
            Logger.log("d", message)

    def closeSplash(self) -> None:
        """Close the splash screen after the application has started."""

        if QtApplication.splash:
            QtApplication.splash.close()
            QtApplication.splash = None

    def createQmlComponent(self, qml_file_path: str, context_properties: Dict[str, "QObject"] = None) -> Optional["QObject"]:
        """Create a QML component from a qml file.
        :param qml_file_path:: The absolute file path to the root qml file.
        :param context_properties:: Optional dictionary containing the properties that will be set on the context of the
        qml instance before creation.
        :return: None in case the creation failed (qml error), else it returns the qml instance.
        :note If the creation fails, this function will ensure any errors are logged to the logging service.
        """

        if self._qml_engine is None: # Protect in case the engine was not initialized yet
            return None
        path = QUrl.fromLocalFile(qml_file_path)
        component = QQmlComponent(self._qml_engine, path)
        result_context = QQmlContext(self._qml_engine.rootContext()) #type: ignore #MyPy doens't realise that self._qml_engine can't be None here.
        if context_properties is not None:
            for name, value in context_properties.items():
                result_context.setContextProperty(name, value)
        result = component.create(result_context)
        for err in component.errors():
            Logger.log("e", str(err.toString()))
        if result is None:
            return None

        # We need to store the context with the qml object, else the context gets garbage collected and the qml objects
        # no longer function correctly/application crashes.
        result.attached_context = result_context
        return result

    @pyqtSlot()
    def deleteAll(self, only_selectable = True) -> None:
        """Delete all nodes containing mesh data in the scene.
        :param only_selectable:. Set this to False to delete objects from all build plates
        """

        self.getController().deleteAllNodesWithMeshData(only_selectable)

    @pyqtSlot()
    def resetWorkspace(self) -> None:
        self._workspace_metadata_storage.clear()
        self.deleteAll()
        self.workspaceLoaded.emit("")

    def getMeshFileHandler(self) -> MeshFileHandler:
        """Get the MeshFileHandler of this application."""

        return self._mesh_file_handler

    def getWorkspaceFileHandler(self) -> WorkspaceFileHandler:
        return self._workspace_file_handler

    @pyqtSlot(result = QObject)
    def getPackageManager(self) -> PackageManager:
        return self._package_manager

    def getHttpRequestManager(self) -> "HttpRequestManager":
        return self._http_network_request_manager

    @classmethod
    def getInstance(cls, *args, **kwargs) -> "QtApplication":
        """Gets the instance of this application.

        This is just to further specify the type of Application.getInstance().
        :return: The instance of this application.
        """

        return cast(QtApplication, super().getInstance(**kwargs))

    def _createSplashScreen(self) -> QSplashScreen:
        return QSplashScreen(QPixmap(Resources.getPath(Resources.Images, self.getApplicationName() + ".png")))

    def _screenScaleFactor(self) -> float:
        # OSX handles sizes of dialogs behind our backs, but other platforms need
        # to know about the device pixel ratio
        if sys.platform == "darwin":
            return 1.0
        else:
            # determine a device pixel ratio from font metrics, using the same logic as UM.Theme
            fontPixelRatio = QFontMetrics(QCoreApplication.instance().font()).ascent() / 11
            # round the font pixel ratio to quarters
            fontPixelRatio = int(fontPixelRatio * 4) / 4
            return fontPixelRatio

    @pyqtProperty(str, constant=True)
    def applicationDisplayName(self) -> str:
        return self.getApplicationDisplayName()


class _QtFunctionEvent(QEvent):
    """Internal.

    Wrapper around a FunctionEvent object to make Qt handle the event properly.
    """

    QtFunctionEvent = QEvent.User + 1

    def __init__(self, fevent: QEvent) -> None:
        super().__init__(self.QtFunctionEvent)
        self._function_event = fevent

