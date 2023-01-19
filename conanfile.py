import os

from pathlib import Path

from conan import ConanFile
from conan.tools.files import copy, mkdir
from conan.tools.microsoft import unix_path
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.52.0"


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

    python_requires = "umbase/[>=0.1.7]@ultimaker/stable", "translationextractor/[>=1.0.0]@ultimaker/stable"
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

    def set_version(self):
        if self.version is None:
            self.version = self._umdefault_version()

    def configure(self):
        self.options["pyarcus"].shared = True
        self.options["cpython"].shared = True

    def validate(self):
        if self.version:
            if Version(self.version) <= Version("4"):
                raise ConanInvalidConfiguration("Only versions 5+ are support")

    def requirements(self):
        for req in self._um_data()["requirements"]:
            self.requires(req)

    def build_requirements(self):
        if self.options.devtools:
            if self.settings.os != "Windows" or self.conf.get("tools.microsoft.bash:path", check_type = str):
                # FIXME: once m4, autoconf, automake are Conan V2 ready use self.win_bash and add gettext as base tool_requirement
                self.tool_requires("gettext/0.21", force_host_context=True)

    @property
    def _base_dir(self):
        if self.install_folder is None:
            if self.build_folder is not None:
                return Path(self.build_folder)
            return Path(os.getcwd(), "venv")
        if self.in_local_cache:
            return Path(self.install_folder)
        else:
            return Path(self.source_folder, "venv")

    @property
    def requirements_txts(self):
        if self.options.devtools:
            return ["requirements.txt", "requirements-dev.txt"]
        return ["requirements.txt"]

    @property
    def _share_dir(self):
        return self._base_dir.joinpath("share")

    @property
    def _script_dir(self):
        if self.settings.os == "Windows":
            return self._base_dir.joinpath("Scripts")
        return self._base_dir.joinpath("bin")

    @property
    def _site_packages(self):
        if self.settings.os == "Windows":
            return self._base_dir.joinpath("Lib", "site-packages")
        py_version = Version(self.deps_cpp_info["cpython"].version)
        return self._base_dir.joinpath("lib", f"python{py_version.major}.{py_version.minor}", "site-packages")

    @property
    def _py_interp(self):
        py_interp = self._script_dir.joinpath(Path(self.deps_user_info["cpython"].python).name)
        if self.settings.os == "Windows":
            py_interp = Path(*[f'"{p}"' if " " in p else p for p in py_interp.parts])
        return py_interp

    def build(self):
        if self.options.devtools:
            if self.settings.os != "Windows" or self.conf.get("tools.microsoft.bash:path", check_type = str):
                # FIXME: once m4, autoconf, automake are Conan V2 ready use self.win_bash and add gettext as base tool_requirement
                for po_file in self.source_path.joinpath("resources", "i18n").glob("**/*.po"):
                    mo_file = self.build_path.joinpath(po_file.with_suffix('.mo').relative_to(self.source_path))
                    mkdir(self, str(unix_path(self, mo_file.parent)))
                    cpp_info = self.dependencies["gettext"].cpp_info
                    self.run(f"{cpp_info.bindirs[0]}/msgfmt {po_file} -o {mo_file} -f", env="conanbuild", ignore_errors=True)

    def generate(self):
        if self.options.devtools:
            if self.settings.os != "Windows" or self.conf.get("tools.microsoft.bash:path", check_type = str):
                # FIXME: once m4, autoconf, automake are Conan V2 ready use self.win_bash and add gettext as base tool_requirement
                # Extract all the new strings and update the existing po files
                extractTool = self.python_requires["translationextractor"].module.ExtractTranslations(self, self.source_path.joinpath("resources", "i18n"), "uranium.pot")
                extractTool.generate()

    def layout(self):
        self.folders.source = "."
        self.folders.build = "venv"
        self.folders.generators = os.path.join(self.folders.build, "conan")

        self.cpp.package.libdirs = [os.path.join("site-packages", "UM")]
        self.cpp.package.resdirs = ["resources", "plugins", "pip_requirements"]  # Note: pip_requirements should be the last item in the list

    def package(self):
        copy(self, "*", src = self.source_path.joinpath("UM"), dst = self.package_path.joinpath(self.cpp.package.libdirs[0]))
        copy(self, "*", src = self.source_path.joinpath("resources"), dst = self.package_path.joinpath(self.cpp.package.resdirs[0]), excludes="*.po")
        copy(self, "*.mo", src = self.build_path.joinpath("resources"), dst = self.package_path.joinpath(self.cpp.package.resdirs[0]))
        copy(self, "*", src = self.source_path.joinpath("plugins"), dst = self.package_path.joinpath(self.cpp.package.resdirs[1]))
        copy(self, "requirement*.txt", src = self.source_path, dst = self.package_path.joinpath(self.cpp.package.resdirs[-1]))

    def package_info(self):
        self.user_info.pip_requirements = "requirements.txt"
        self.user_info.pip_requirements_build = "requirements-dev.txt"

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

        del self.info.options.devtools
