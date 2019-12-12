from PyQt5.QtCore import QObject
from UM.FlameProfiler import pyqtSlot
from typing import Dict, Any, Optional


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
    def __init__(self, container: Dict[str, Any], parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._container = container

    @pyqtSlot(str, result = "QVariant")
    def getValue(self, value: str):
        return self._container.get(value, None)

    @pyqtSlot(str, result="QVariantList")
    def getValueList(self, value: str):
        return self._container.get(value, None)

    @pyqtSlot(str, "QVariant")
    def setValue(self, key: str, value: Any) -> None:
        self._container[key] = value

    @pyqtSlot(result = int)
    def getCount(self) -> int:
        return len(self._container)
