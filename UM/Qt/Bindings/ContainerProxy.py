from PyQt5.QtCore import QObject
from UM.FlameProfiler import pyqtSlot

# This class wraps a Python container and provides access to its elements
#
# It is primarily intended as a reasonably fast wrapper around containers
# that need to be updated and need to notify QML of their changes.
#
# To use it, define a property that returns a QObject with a notify signal.
# From the property getter, return an instance of this object. Whenever the
# contents of the container change, simply emit the notify signal, do not
# recreate the proxy.
class ContainerProxy(QObject):
    def __init__(self, container, parent = None):
        super().__init__(parent)

        self._container = container

    @pyqtSlot(str, result = "QVariant")
    def getValue(self, value):
        return self._container.get(value, None)

    @pyqtSlot(str, "QVariant")
    def setValue(self, key, value):
        self._container[key] = value

    @pyqtSlot(result = int)
    def getCount(self):
        return len(self._container)
