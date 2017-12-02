# Copyright (c) 2017 Thomas Karl Pietrowski

import warnings

import .Utils as Factory

Factory.importQtModule("QtCore", globals())

if Factory.imported_binding is Factory.QtBinding.PyQt5:
    Signal = pyqtSignal
    Slot = pyqtSignal
    Property = pyqtProperty
    
    def pyqtSignal(self, *args, **kwargs):
        warnings.warn("Usage of pyqtSignal is deprecated! Please use Signal instead!")
        return Signal(*args, **kwargs)
    
    def pyqtSlot(self, *args, **kwargs):
        warnings.warn("Usage of pyqtSlot is deprecated! Please use Slot instead!")
        return Slot(*args, **kwargs)
    
    def pyqtProperty(self, *args, **kwargs):
        warnings.warn("Usage of pyqtProperty is deprecated! Please use Property instead!")
        return Property(*args, **kwargs)