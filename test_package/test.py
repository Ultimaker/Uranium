import sys

if sys.platform == "win32":
    # On Windows ARM64, Python's import mechanism uses LoadLibraryExW with
    # LOAD_LIBRARY_SEARCH_DEFAULT_DIRS which does NOT search PATH.
    # Two components needed by PyQt6 are only accessible via PATH:
    #   1. python3.dll - the stable ABI DLL (conan cpython loads python312.dll, not python3.dll)
    #   2. Qt6 DLLs in PyQt6\Qt6\bin\
    # Pre-loading them via ctypes (which uses LoadLibraryW legacy path search)
    # puts them in the process module table where LoadLibraryExW finds them as already-loaded.
    import ctypes, os, importlib.util
    ctypes.windll.kernel32.LoadLibraryW("python3.dll")
    _spec = importlib.util.find_spec("PyQt6")
    if _spec and _spec.submodule_search_locations:
        _qt6_bin = os.path.join(list(_spec.submodule_search_locations)[0], "Qt6", "bin")
        for _dll in ["Qt6Core.dll", "Qt6Network.dll", "Qt6DBus.dll", "Qt6Gui.dll", "Qt6Widgets.dll"]:
            ctypes.windll.kernel32.LoadLibraryW(os.path.join(_qt6_bin, _dll))

import UM

from UM import Util

print(Util.parseBool("True"))
