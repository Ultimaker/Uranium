import os

from pathlib import Path

from conan import ConanFile
from conans import tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.47.0"


class UraniumConan(ConanFile):
    name = "uranium"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/uranium"
    description = "A Python framework for building Desktop applications."
    topics = ("conan", "python", "pyqt5", "qt", "3d-graphics", "3d-models", "python-framework")
    build_policy = "missing"
    exports = "LICENSE*"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    python_requires = "umbase/0.1.2@ultimaker/testing"
    python_requires_extend = "umbase.UMBaseConanfile"

    options = {
        "devtools": [True, False]
    }
    default_options = {
        "devtools": False,
    }
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": "auto",
        "revision": "auto"
    }

    def configure(self):
        self.options["arcus"].shared = True
        self.options["cpython"].shared = True

    def validate(self):
        if self.version:
            if tools.Version(self.version) <= tools.Version("4"):
                raise ConanInvalidConfiguration("Only versions 5+ are support")

    def requirements(self):
        for req in self._um_data(self.version)["requirements"]:
            self.requires(req)

    def generate(self):
        pass

    def layout(self):
        self.folders.source = "."
        self.folders.build = "venv"
        self.folders.generators = os.path.join(self.folders.build, "conan")

        self.cpp.package.libdirs = [os.path.join("site-packages", "UM")]
        self.cpp.package.resdirs = ["resources", "plugins", "pip_requirements"]  # Note: pip_requirements should be the last item in the list

    def package(self):
        self.copy("*", src = "UM", dst = self.cpp.package.libdirs[0])
        self.copy("*", src = "resources", dst = self.cpp.package.resdirs[0])
        self.copy("*", src = "plugins", dst = self.cpp.package.resdirs[1])

    def package_info(self):
        #  TODO: Add Uranium specific requirements.txt's and add these to the user_info
        if self.in_local_cache:
            self.runenv_info.append_path("PYTHONPATH", str(Path(self.cpp_info.lib_paths[0]).parent))
            self.runenv_info.append_path("PYTHONPATH", self.cpp_info.res_paths[1])
        else:
            self.runenv_info.append_path("PYTHONPATH", self.source_folder)
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.source_folder, "plugins"))

    def package_id(self):
        del self.info.settings.os
        del self.info.settings.compiler
        del self.info.settings.build_type
        del self.info.settings.arch
