# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import sys
import os
import signal


from PyQt5.QtCore import Qt, QCoreApplication, QEvent, QUrl, pyqtProperty, pyqtSignal, pyqtSlot, QLocale, QTranslator, QLibraryInfo, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox, QSystemTrayIcon
from PyQt5.QtGui import QGuiApplication, QIcon, QPixmap, QFontMetrics
from PyQt5.QtCore import QTimer

from UM.FileHandler.ReadFileJob import ReadFileJob
from UM.Application import Application
from UM.Qt.QtRenderer import QtRenderer
from UM.Qt.Bindings.Bindings import Bindings
from UM.Signal import Signal, signalemitter
from UM.Resources import Resources
from UM.Logger import Logger
from UM.Preferences import Preferences
from UM.i18n import i18nCatalog
from UM.JobQueue import JobQueue
from UM.View.GL.OpenGLContext import OpenGLContext
import UM.Settings.InstanceContainer  # For version upgrade to know the version number.
import UM.Settings.ContainerStack  # For version upgrade to know the version number.
import UM.Preferences  # For version upgrade to know the version number.
import UM.VersionUpgradeManager
from UM.Mesh.ReadMeshJob import ReadMeshJob

import UM.Qt.Bindings.Theme
from UM.PluginRegistry import PluginRegistry


# Raised when we try to use an unsupported version of a dependency.
class UnsupportedVersionError(Exception):
    pass

# Check PyQt version, we only support 5.4 or higher.
major, minor = PYQT_VERSION_STR.split(".")[0:2]
if int(major) < 5 or int(minor) < 4:
    raise UnsupportedVersionError("This application requires at least PyQt 5.4.0")


##  Application subclass that provides a Qt application object.
@signalemitter
class QtApplication(QApplication, Application):

    def __init__(self, tray_icon_name = None, **kwargs):
        plugin_path = ""
        if sys.platform == "win32":
            if hasattr(sys, "frozen"):
                plugin_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "PyQt5", "plugins")
                Logger.log("i", "Adding QT5 plugin path: %s" % (plugin_path))
                QCoreApplication.addLibraryPath(plugin_path)
            else:
                import site
                for dir in site.getsitepackages():
                    QCoreApplication.addLibraryPath(os.path.join(dir, "PyQt5", "plugins"))
        elif sys.platform == "darwin":
            plugin_path = os.path.join(Application.getInstallPrefix(), "Resources", "plugins")

        if plugin_path:
            Logger.log("i", "Adding QT5 plugin path: %s" % (plugin_path))
            QCoreApplication.addLibraryPath(plugin_path)

        os.environ["QSG_RENDER_LOOP"] = "basic"

        super().__init__(sys.argv, **kwargs)

        self.setAttribute(Qt.AA_UseDesktopOpenGL)
        major_version, minor_version, profile = OpenGLContext.detectBestOpenGLVersion()

        if major_version is None and minor_version is None and profile is None:
            Logger.log("e", "Startup failed because OpenGL version probing has failed: tried to create a 2.0 and 4.1 context. Exiting")
            QMessageBox.critical(None, "Failed to probe OpenGL",
                "Could not probe OpenGL. This program requires OpenGL 2.0 or higher. Please check your video card drivers.")
            sys.exit(1)
        else:
            Logger.log("d", "Detected most suitable OpenGL context version: %s" % (
                OpenGLContext.versionAsText(major_version, minor_version, profile)))
        OpenGLContext.setDefaultFormat(major_version, minor_version, profile = profile)

        self._plugins_loaded = False  # Used to determine when it's safe to use the plug-ins.
        self._main_qml = "main.qml"
        self._engine = None
        self._renderer = None
        self._main_window = None
        self._theme = None

        self._shutting_down = False
        self._qml_import_paths = []
        self._qml_import_paths.append(os.path.join(os.path.dirname(sys.executable), "qml"))
        self._qml_import_paths.append(os.path.join(Application.getInstallPrefix(), "Resources", "qml"))

        try:
            self._splash = self._createSplashScreen()
        except FileNotFoundError:
            self._splash = None
        else:
            self._splash.show()
            self.processEvents()

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # This is done here as a lot of plugins require a correct gl context. If you want to change the framework,
        # these checks need to be done in your <framework>Application.py class __init__().

        i18n_catalog = i18nCatalog("uranium")

        self.showSplashMessage(i18n_catalog.i18nc("@info:progress", "Loading plugins..."))
        self._loadPlugins()
        self.parseCommandLine()
        Logger.log("i", "Command line arguments: %s", self._parsed_command_line)
        self._plugin_registry.checkRequiredPlugins(self.getRequiredPlugins())

        self.showSplashMessage(i18n_catalog.i18nc("@info:progress", "Updating configuration..."))
        upgraded = UM.VersionUpgradeManager.VersionUpgradeManager.getInstance().upgrade()
        if upgraded:
            # Preferences might have changed. Load them again.
            # Note that the language can't be updated, so that will always revert to English.
            preferences = Preferences.getInstance()
            try:
                preferences.readFromFile(Resources.getPath(Resources.Preferences, self._application_name + ".cfg"))
            except FileNotFoundError:
                pass

        self.showSplashMessage(i18n_catalog.i18nc("@info:progress", "Loading preferences..."))
        try:
            file = Resources.getPath(Resources.Preferences, self.getApplicationName() + ".cfg")
            Preferences.getInstance().readFromFile(file)
        except FileNotFoundError:
            pass

        self.getApplicationName()

        Preferences.getInstance().addPreference("%s/recent_files" % self.getApplicationName(), "")

        self._recent_files = []
        files = Preferences.getInstance().getValue("%s/recent_files" % self.getApplicationName()).split(";")
        for f in files:
            if not os.path.isfile(f):
                continue

            self._recent_files.append(QUrl.fromLocalFile(f))

        JobQueue.getInstance().jobFinished.connect(self._onJobFinished)

        # Initialize System tray icon and make it invisible because it is used only to show pop up messages
        self._tray_icon = None
        self._tray_icon_widget = None
        if tray_icon_name:
            self._tray_icon = QIcon(Resources.getPath(Resources.Images, tray_icon_name))
            self._tray_icon_widget = QSystemTrayIcon(self._tray_icon)
            self._tray_icon_widget.setVisible(False)

    recentFilesChanged = pyqtSignal()

    @pyqtProperty("QVariantList", notify=recentFilesChanged)
    def recentFiles(self):
        return self._recent_files

    def _onJobFinished(self, job):
        if (not isinstance(job, ReadMeshJob) and not isinstance(job, ReadFileJob)) or not job.getResult():
            return

        f = QUrl.fromLocalFile(job.getFileName())
        if f in self._recent_files:
            self._recent_files.remove(f)

        self._recent_files.insert(0, f)
        if len(self._recent_files) > 10:
            del self._recent_files[10]

        pref = ""
        for path in self._recent_files:
            pref += path.toLocalFile() + ";"

        Preferences.getInstance().setValue("%s/recent_files" % self.getApplicationName(), pref)
        self.recentFilesChanged.emit()

    def run(self):
        pass

    def hideMessage(self, message):
        with self._message_lock:
            if message in self._visible_messages:
                self._visible_messages.remove(message)
                self.visibleMessageRemoved.emit(message)

    def showMessage(self, message):
        with self._message_lock:
            if message not in self._visible_messages:
                self._visible_messages.append(message)
                message.setLifetimeTimer(QTimer())
                message.setInactivityTimer(QTimer())
                self.visibleMessageAdded.emit(message)

        # also show toast message when the main window is minimized
        self.showToastMessage(self._application_name, message.getText())

    def _onMainWindowStateChanged(self, window_state):
        if self._tray_icon:
            visible = window_state == Qt.WindowMinimized
            self._tray_icon_widget.setVisible(visible)

    # Show toast message using System tray widget.
    def showToastMessage(self, title: str, message: str):
        if self.checkWindowMinimizedState() and self._tray_icon_widget:
            # NOTE: Qt 5.8 don't support custom icon for the system tray messages, but Qt 5.9 does.
            #       We should use the custom icon when we switch to Qt 5.9
            self._tray_icon_widget.showMessage(title, message)

    def setMainQml(self, path):
        self._main_qml = path

    def initializeEngine(self):
        # TODO: Document native/qml import trickery
        Bindings.register()

        self._engine = QQmlApplicationEngine()

        for path in self._qml_import_paths:
            self._engine.addImportPath(path)

        if not hasattr(sys, "frozen"):
            self._engine.addImportPath(os.path.join(os.path.dirname(__file__), "qml"))

        self._engine.rootContext().setContextProperty("QT_VERSION_STR", QT_VERSION_STR)
        self._engine.rootContext().setContextProperty("screenScaleFactor", self._screenScaleFactor())

        self.registerObjects(self._engine)

        self._engine.load(self._main_qml)
        self.engineCreatedSignal.emit()

    engineCreatedSignal = Signal()

    def isShuttingDown(self):
        return self._shutting_down

    def registerObjects(self, engine):
        engine.rootContext().setContextProperty("PluginRegistry", PluginRegistry.getInstance())

    def getRenderer(self):
        if not self._renderer:
            self._renderer = QtRenderer()

        return self._renderer

    @classmethod
    def addCommandLineOptions(self, parser):
        super().addCommandLineOptions(parser)
        parser.add_argument("--disable-textures",
                            dest="disable-textures",
                            action="store_true", default=False,
                            help="Disable Qt texture loading as a workaround for certain crashes.")
        parser.add_argument("-qmljsdebugger", help="For Qt's QML debugger compatibility")

    mainWindowChanged = Signal()

    def getMainWindow(self):
        return self._main_window

    def setMainWindow(self, window):
        if window != self._main_window:
            if self._main_window is not None:
                self._main_window.windowStateChanged.disconnect(self._onMainWindowStateChanged)

            self._main_window = window

            if self._main_window is not None:
                self._main_window.windowStateChanged.connect(self._onMainWindowStateChanged)

            self.mainWindowChanged.emit()

    def getTheme(self):
        if self._theme is None:
            if self._engine is None:
                Logger.log("e", "The theme cannot be accessed before the engine is initialised")
                return None

            self._theme = UM.Qt.Bindings.Theme.Theme.getInstance(self._engine)
        return self._theme

    #   Handle a function that should be called later.
    def functionEvent(self, event):
        e = _QtFunctionEvent(event)
        QCoreApplication.postEvent(self, e)

    #   Handle Qt events
    def event(self, event):
        if event.type() == _QtFunctionEvent.QtFunctionEvent:
            event._function_event.call()
            return True

        return super().event(event)

    def windowClosed(self):
        Logger.log("d", "Shutting down %s", self.getApplicationName())
        self._shutting_down = True

        try:
            Preferences.getInstance().writeToFile(Resources.getStoragePath(Resources.Preferences, self.getApplicationName() + ".cfg"))
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

        self.quit()

    def checkWindowMinimizedState(self):
        if self._main_window is not None and self._main_window.windowState() == Qt.WindowMinimized:
            return True
        else:
            return False

    ##  Get the backend of the application (the program that does the heavy lifting).
    #   The backend is also a QObject, which can be used from qml.
    #   \returns Backend \type{Backend}
    @pyqtSlot(result="QObject*")
    def getBackend(self):
        return self._backend

    ##  Load a Qt translation catalog.
    #
    #   This method will locate, load and install a Qt message catalog that can be used
    #   by Qt's translation system, like qsTr() in QML files.
    #
    #   \param file The file name to load, without extension. It will be searched for in
    #               the i18nLocation Resources directory. If it can not be found a warning
    #               will be logged but no error will be thrown.
    #   \param language The language to load translations for. This can be any valid language code
    #                   or 'default' in which case the language is looked up based on system locale.
    #                   If the specified language can not be found, this method will fall back to
    #                   loading the english translations file.
    #
    #   \note When `language` is `default`, the language to load can be changed with the
    #         environment variable "LANGUAGE".
    def loadQtTranslation(self, file, language = "default"):
        # TODO Add support for specifying a language from preferences
        path = None
        if language == "default":
            path = self._getDefaultLanguage(file)
        else:
            path = Resources.getPath(Resources.i18n, language, "LC_MESSAGES", file + ".qm")

        # If all else fails, fall back to english.
        if not path:
            Logger.log("w", "Could not find any translations matching {0} for file {1}, falling back to english".format(language, file))
            try:
                path = Resources.getPath(Resources.i18n, "en_US", "LC_MESSAGES", file + ".qm")
            except FileNotFoundError:
                Logger.log("w", "Could not find English translations for file {0}. Switching to developer english.".format(file))
                return

        translator = QTranslator()
        if not translator.load(path):
            Logger.log("e", "Unable to load translations %s", file)
            return

        # Store a reference to the translator.
        # This prevents the translator from being destroyed before Qt has a chance to use it.
        self._translators[file] = translator

        # Finally, install the translator so Qt can use it.
        self.installTranslator(translator)

    ##  Display text on the splash screen.
    def showSplashMessage(self, message):
        if self._splash:
            self._splash.showMessage(message , Qt.AlignHCenter | Qt.AlignVCenter)
            self.processEvents()

    ##  Close the splash screen after the application has started.
    def closeSplash(self):
        if self._splash:
            self._splash.close()
            self._splash = None

    def _createSplashScreen(self):
        return QSplashScreen(QPixmap(Resources.getPath(Resources.Images, self.getApplicationName() + ".png")))

    def _screenScaleFactor(self):
        # OSX handles sizes of dialogs behind our backs, but other platforms need
        # to know about the device pixel ratio
        if sys.platform == "darwin":
            return 1.0
        else:
            # determine a device pixel ratio from font metrics, using the same logic as UM.Theme
            fontPixelRatio = QFontMetrics(QCoreApplication.instance().font()).ascent() / 11
            # round the font pixel ratio to quarters
            fontPixelRatio = int(fontPixelRatio * 4)/4
            return fontPixelRatio

    def _getDefaultLanguage(self, file):
        # If we have a language override set in the environment, try and use that.
        lang = os.getenv("URANIUM_LANGUAGE")
        if lang:
            try:
                return Resources.getPath(Resources.i18n, lang, "LC_MESSAGES", file + ".qm")
            except FileNotFoundError:
                pass

        # Else, try and get the current language from preferences
        lang = Preferences.getInstance().getValue("general/language")
        if lang:
            try:
                return Resources.getPath(Resources.i18n, lang, "LC_MESSAGES", file + ".qm")
            except FileNotFoundError:
                pass

        # If none of those are set, try to use the environment's LANGUAGE variable.
        lang = os.getenv("LANGUAGE")
        if lang:
            try:
                return Resources.getPath(Resources.i18n, lang, "LC_MESSAGES", file + ".qm")
            except FileNotFoundError:
                pass

        # If looking up the language from the enviroment or preferences fails, try and use Qt's system locale instead.
        locale = QLocale.system()

        # First, try and find a directory for any of the provided languages
        for lang in locale.uiLanguages():
            try:
                return Resources.getPath(Resources.i18n, lang, "LC_MESSAGES", file + ".qm")
            except FileNotFoundError:
                pass

        # If that fails, see if we can extract a language code from the
        # preferred language, regardless of the country code. This will turn
        # "en-GB" into "en" for example.
        lang = locale.uiLanguages()[0]
        lang = lang[0:lang.find("-")]
        for subdirectory in os.path.listdir(Resources.getPath(Resources.i18n)):
            if subdirectory == "en_7S": #Never automatically go to Pirate.
                continue
            if not os.path.isdir(Resources.getPath(Resources.i18n, subdirectory)):
                continue
            if subdirectory.startswith(lang + "_"): #Only match the language code, not the country code.
                return Resources.getPath(Resources.i18n, lang, "LC_MESSAGES", file + ".qm")

        return None


##  Internal.
#
#   Wrapper around a FunctionEvent object to make Qt handle the event properly.
class _QtFunctionEvent(QEvent):
    QtFunctionEvent = QEvent.User + 1

    def __init__(self, fevent):
        super().__init__(self.QtFunctionEvent)
        self._function_event = fevent

