import os

from platform import python_version

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

    python_requires = "umbase/0.1@ultimaker/testing"
    python_requires_extend = "umbase.UMBaseConanfile"

    options = {
        "python_version": "ANY",
        "devtools": [True, False]
    }
    default_options = {
        "python_version": "system",
        "devtools": False,
    }
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": "auto",
        "revision": "auto"
    }

    def config_options(self):
        if self.options.python_version == "system":
            self.options.python_version = python_version()

    def configure(self):
        self.options["*"].shared = True
        self.options["*"].python_version = self.options.python_version

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
        self.folders.venv = "venv"
        self.folders.generators = os.path.join(self.folders.build, "conan")

        self.cpp.package.libdirs = ["site-packages"]

    def package(self):
        self.copy("*", src = "UM", dst = os.path.join(self.cpp.package.libdirs[0], "UM"))
        self.copy("*", src = "plugins", dst = os.path.join(self.cpp.package.libdirs[0], "plugins"))
        self.copy("*", src = "resources", dst = os.path.join(self.cpp.package.resdirs[0], "resources"))

    def package_info(self):
        if self.in_local_cache:
            self.runenv_info.append_path("PYTHONPATH", self.cpp_info.libdirs[0])
        else:
            self.runenv_info.append_path("PYTHONPATH", self.source_folder)

    def package_id(self):
        del self.info.settings.os
        del self.info.settings.compiler
        del self.info.settings.build_type
        del self.info.settings.arch
