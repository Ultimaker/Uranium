from io import StringIO

from conan import ConanFile
from conan.tools.env import VirtualRunEnv
from conan.tools.build import can_run
from conan.errors import ConanException
from conan.tools.files import copy


class UraniumTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        venv = VirtualRunEnv(self)
        venv.generate()

        cpp_info = self.dependencies[self.tested_reference_str].cpp_info
        copy(self, "*.pyd", src=cpp_info.libdirs[0], dst=self.build_folder)

        for dep in self.dependencies.values():
            for bin_dir in dep.cpp_info.bindirs:
                copy(self, "*.dll", src=bin_dir, dst=self.build_folder)

    def test(self):
        if can_run(self):
            test_buf = StringIO()
            self.run(f"python test.py", env="conanrun", stdout=test_buf, scope="run")
            if "True" not in test_buf.getvalue():
                raise ConanException("Uranium wasn't build correctly!")
