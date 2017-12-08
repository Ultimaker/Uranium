# Copyright (c) 2017 Thomas Karl Pietrowski

import warnings

from UM.Qt.Factory import Utils

Utils.importQtModule("QtCore", globals())

if Utils.imported_binding is Utils.QtBinding.PyQt5:
    Signal = pyqtSignal
    Slot = pyqtSlot
    Property = pyqtProperty
    
    """
    def pyqtSignal(*args, **kwargs):
        warnings.warn("Usage of pyqtSignal is deprecated! Please use Signal instead!")
        return Signal(*args, **kwargs)
    
    def pyqtSlot(*args, **kwargs):
        warnings.warn("Usage of pyqtSlot is deprecated! Please use Slot instead!")
        return Slot(*args, **kwargs)
    
    def pyqtProperty(*args, **kwargs):
        warnings.warn("Usage of pyqtProperty is deprecated! Please use Property instead!")
        return Property(*args, **kwargs)
    """

if Utils.imported_binding is Utils.QtBinding.PySide2:
    import PySide2
    pyqtSignal = Signal
    pyqtSlot = Slot
    pyqtProperty = Property
    
    PYQT_VERSION_STR = PySide2.__version__
    QT_VERSION_STR = __version__