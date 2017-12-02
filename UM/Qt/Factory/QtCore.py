# Copyright (c) 2017 Thomas Karl Pietrowski

import Utils as Factory

Factory.importQtModule("QtCore", globals())

if Factory.imported_binding is Factory.QtBinding.PyQt5:
    Signal = pyqtSignal
    Slot = pyqtSignal
    Property = pyqtProperty