import sys
import os
import signal
import platform

from PyQt5.QtCore import Qt, QObject, QCoreApplication, QEvent, pyqtSlot, QLocale, QTranslator, QLibraryInfo
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType, qmlRegisterSingletonType
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QGuiApplication, QPixmap
from PyQt5.QtCore import QTimer

from UM.Application import Application
from UM.Qt.QtGL2Renderer import QtGL2Renderer
from UM.Qt.Bindings.Bindings import Bindings
from UM.JobQueue import JobQueue
from UM.Signal import Signal, SignalEmitter
from UM.Resources import Resources
from UM.Logger import Logger
from UM.Preferences import Preferences

##  Application subclass that provides a Qt application object.
class QtApplication(QApplication, Application, SignalEmitter):
    def __init__(self, **kwargs):
        if hasattr(sys, 'frozen') and sys.platform == 'win32':
            plugin_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), 'PyQt5', 'plugins')
            Logger.log('i', 'Adding QT5 plugin path: %s' % (plugin_path))
            QCoreApplication.addLibraryPath(plugin_path)
        super().__init__(sys.argv, **kwargs)

        self._mainQml = "main.qml"
        self._engine = None
        self._renderer = None

        try:
            self._splash = QSplashScreen(QPixmap(Resources.getPath(Resources.ImagesLocation, self.getApplicationName() + ".png")))
        except FileNotFoundError:
            self._splash = None
        else:
            self._splash.show()
            self.processEvents()

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # This is done here as a lot of plugins require a correct gl context. If you want to change the framework,
        # these checks need to be done in your <framework>Application.py class __init__().

        self.showSplashMessage('Loading plugins...')
        self._loadPlugins()
        self._plugin_registry.checkRequiredPlugins(self.getRequiredPlugins())

        self.showSplashMessage('Loading machines...')
        self.loadMachines()

        self.showSplashMessage('Loading preferences...')
        try:
            file = Resources.getPath(Resources.PreferencesLocation, self.getApplicationName() + '.cfg')
            Preferences.getInstance().readFromFile(file)
        except FileNotFoundError:
            pass

        self._translators = {}

        self.showSplashMessage('Loading translations...')

        self.loadQtTranslation('uranium_qt')
        self.loadQtTranslation(self.getApplicationName() + '_qt')

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
                message.setTimer(QTimer())
                self.visibleMessageAdded.emit(message)
    
        pass

    def setMainQml(self, base_path, qml_file):
        if hasattr(sys, 'frozen'):
            self._mainQml = os.path.join(os.path.dirname(sys.executable), qml_file)
        else:
            self._mainQml = os.path.join(base_path, qml_file)

    def initializeEngine(self):
        # TODO: Document native/qml import trickery
        Bindings.register()

        self._engine = QQmlApplicationEngine()
        self.engineCreatedSignal.emit()
        if hasattr(sys, 'frozen'):
            self._engine.addImportPath(os.path.join(os.path.dirname(sys.executable), 'qml'))
        else:
            self._engine.addImportPath(os.path.join(os.path.dirname(__file__), 'qml'))

        self.registerObjects(self._engine)
        
        self._engine.load(self._mainQml)
    
    engineCreatedSignal = Signal()
    
    def registerObjects(self, engine):
        pass

    def getRenderer(self):
        if not self._renderer:
            self._renderer = QtGL2Renderer()

        return self._renderer

    #   Overridden from QApplication::setApplicationName to call our internal setApplicationName
    def setApplicationName(self, name):
        Application.setApplicationName(self, name)

    #   Handle a function that should be called later.
    def functionEvent(self, event):
        e = _QtFunctionEvent(event)
        QCoreApplication.postEvent(self, e)

    #   Handle Qt events
    def event(self, event):
        if event.type() == _QtFunctionEvent.QtFunctionEvent:
            event.functionEvent.call()
            return True

        return super().event(event)

    def windowClosed(self):
        self.getBackend().close()
        self.quit()
        self.saveMachines()
        Preferences.getInstance().writeToFile(Resources.getStoragePath(Resources.PreferencesLocation, self.getApplicationName() + '.cfg'))

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
    def loadQtTranslation(self, file, language = 'default'):
        #TODO Add support for specifying a language from preferences
        path = None
        if language == 'default':
            # If we have a language set in the environment, try and use that.
            lang = os.getenv('LANGUAGE')
            if lang:
                try:
                    path = Resources.getPath(Resources.i18nLocation, lang, 'LC_MESSAGES', file + '.qm')
                except FileNotFoundError:
                    path = None

            # If looking up the language from the enviroment fails, try and use Qt's system locale instead.
            if not path:
                locale = QLocale.system()

                # First, try and find a directory for any of the provided languages
                for lang in locale.uiLanguages():
                    try:
                        path = Resources.getPath(Resources.i18nLocation, lang, "LC_MESSAGES", file + '.qm')
                        language = lang
                    except FileNotFoundError:
                        pass
                    else:
                        break

                # If that fails, see if we can extract a language "class" from the
                # preferred language. This will turn "en-GB" into "en" for example.
                if not path:
                    lang = locale.uiLanguages()[0]
                    lang = lang[0:lang.find('-')]
                    try:
                        path = Resources.getPath(Resources.i18nLocation, lang, "LC_MESSAGES", file + '.qm')
                        language = lang
                    except FileNotFoundError:
                        pass
        else:
            path = Resources.getPath(Resources.i18nLocation, language, "LC_MESSAGES", file + '.qm')

        # If all else fails, fall back to english.
        if not path:
            Logger.log('w', "Could not find any translations matching {0} for file {1}, falling back to english".format(language, file))
            try:
                path = Resources.getPath(Resources.i18nLocation, 'en', 'LC_MESSAGES', file + '.qm')
            except FileNotFoundError:
                Logger.log('w', "Could not find English translations for file {0}. Switching to developer english.".format(file))
                return

        translator = QTranslator()
        if not translator.load(path):
            Logger.log('e', "Unable to load translations %s", file)
            return

        # Store a reference to the translator.
        # This prevents the translator from being destroyed before Qt has a chance to use it.
        self._translators[file] = translator

        # Finally, install the translator so Qt can use it.
        self.installTranslator(translator)

    ##  Display text on the splash screen.
    def showSplashMessage(self, message):
        if self._splash:
            self._splash.showMessage(message , Qt.AlignHCenter | Qt.AlignBottom)
            self.processEvents()

    ##  Close the splash screen after the application has started.
    def closeSplash(self):
        if self._splash:
            self._splash.close()
            self._splash = None

##  Internal.
#
#   Wrapper around a FunctionEvent object to make Qt handle the event properly.
class _QtFunctionEvent(QEvent):
    QtFunctionEvent = QEvent.User + 1

    def __init__(self, fevent):
        super().__init__(self.QtFunctionEvent)
        self.functionEvent = fevent

