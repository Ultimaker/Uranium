import shutil

from io import StringIO
from pathlib import Path

from conan import ConanFile
from conan.tools.env import VirtualRunEnv
from conans import tools
from conans.errors import ConanException

class UraniumTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"

    def generate(self):
        venv = VirtualRunEnv(self)
        venv.generate()

    def build(self):
        if not tools.cross_building(self):
            shutil.copy(Path(self.source_folder).joinpath("test.py"), Path(self.build_folder).joinpath("test.py"))

    def imports(self):
        if self.settings.os == "Windows" and not tools.cross_building(self, skip_x64_x86 = True):
            self.copy("*.pyd", dst=".", src="@libdirs")

    def test(self):
        if not tools.cross_building(self):
            test_buf = StringIO()
            try:
                self.run(f"python test.py", env="conanrun", output=test_buf)
            except Exception:
                print(test_buf.getvalue())
                raise ConanException("Uranium wasn't build correctly!")

            if "True" not in test_buf.getvalue():
                raise ConanException("Uranium wasn't build correctly!")
