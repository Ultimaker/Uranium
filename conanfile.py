import os
import pathlib

from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake


class UraniumConan(ConanFile):
    name = "Uranium"
    version = "4.10.0"
    license = "LGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/uranium"
    description = "A Python framework for building Desktop applications."
    topics = ("conan", "python", "pyqt5", "qt", "3d-graphics", "3d-models", "python-framework")
    settings = "os", "compiler", "build_type", "arch"
    exports = "LICENSE"
    options = {
        "python_version": "ANY"
    }
    default_options = {
        "python_version": "3.8"
    }
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": "auto",
        "revision": "auto"
    }

    def configure(self):
        self.options["Arcus"].python_version = self.options.python_version

    def build_requirements(self):
        self.build_requires("cmake/[>=3.16.2]")

    def requirements(self):
        self.requires(f"Arcus/4.10.0@ultimaker/testing")

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        tc = CMakeToolchain(self)
        tc.variables["Python_VERSION"] = self.options.python_version
        tc.generate()

    _cmake = None

    def configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        cmake.install()
        self.copy("*", src = os.path.join(self.package_folder, "lib", f"python{self.options.python_version}",
                                          "site-packages"), dst = "site-packages")
        self.copy("*", src = os.path.join(self.package_folder, "lib", "uranium"), dst = "site-packages")
        self.copy("*.cmake", src = os.path.join(self.package_folder, "share"), dst = "cmake", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_info(self):
        if self.in_local_cache:
            self.user_info.URANIUM_CMAKE_PATH = str(os.path.join(self.package_folder, "cmake"))
            self.runenv_info.prepend_path("PYTHONPATH", os.path.join(self.package_folder, "site-packages"))
        else:
            self.user_info.URANIUM_CMAKE_PATH = str(os.path.join(str(pathlib.Path(__file__).parent.absolute()), "cmake"))
            self.runenv_info.prepend_path("PYTHONPATH",  str(pathlib.Path(__file__).parent.absolute()))

    def package_id(self):
        self.info.header_only()
