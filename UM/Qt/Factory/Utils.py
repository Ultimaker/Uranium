# Copyright (c) 2017 Thomas Karl Pietrowski

import importlib
import os

from UM.Logger import Logger

class QtBinding:
    PyQt5 = "PyQt5"
    PySide2 = "PySide2"

if "URANIUM_QT" in os.environ.keys():
    Logger.log("d", "Using URANIUM_QT: ", repr(os.environ["URANIUM_QT"]))
    __import__(os.environ["URANIUM_QT"])
    imported_binding = os.environ["URANIUM_QT"]
else:
    imported_binding = None

if not imported_binding:
    for binding in [QtBinding.PySide2,
                    QtBinding.PyQt5,
                    ]:
        try:
            __import__(binding)
            imported_binding = binding
            break
        except:
            continue

if not imported_binding:
    raise ImportError("Could not find any Qt binding!")
else:
    Logger.log("d", "Using Qt binding: {}".format(imported_binding))

def importQtModule(name, _globals = None):
    if not _globals:
        _globals = globals()
    name = "{}.{}".format(imported_binding, name)
    imported_module = importlib.import_module(name) # This could fail!
    _globals.update(imported_module.__dict__)
    """
    test = __import__('os',globals(),locals())
    for k in dir(test):
        globals()[k] = test.__dict__[k]
    """

