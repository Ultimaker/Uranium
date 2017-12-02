# Copyright (c) 2017 Thomas Karl Pietrowski

import importlib

class QtBinding:
    PyQt5 = "PyQt5"
    PySide2 = "PySide2"

imported_binding = None

try:
    import PyQt5
    imported_binding = QtBinding.PyQt5
except:
    pass

try:
    import PySide2
    imported_binding = QtBinding.PySide2
except:
    pass

if not imported_binding:
    raise ImportError("Could not find any Qt binding!")

def importQtModule(name):
    name = "{}.{}".format(imported_binding, name)
    imported_module = importlib.import_module(name) # This could fail!
    globals().update(imported_module.__dict__)
    """
    test = __import__('os',globals(),locals())
    for k in dir(test):
        globals()[k] = test.__dict__[k]
    """

