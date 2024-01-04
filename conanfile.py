import os

from pathlib import Path

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, mkdir
from conan.tools.microsoft import unix_path
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.58.0 <2.0.0"


class UraniumConan(ConanFile):
    name = "uranium"
    license = "LGPL-3.0"
    author = "UltiMaker"
    url = "https://github.com/Ultimaker/uranium"
    description = "A Python framework for building Desktop applications."
    topics = ("conan", "python", "pyqt6", "qt", "3d-graphics", "3d-models", "python-framework")
    exports = "LICENSE*"
    settings = "os", "compiler", "build_type", "arch"

    python_requires = "umbase/[>=0.1.7]@ultimaker/stable", "translationextractor/[>=2.2.0]@ultimaker/stable"
    python_requires_extend = "umbase.UMBaseConanfile"

    options = {
        "devtools": [True, False],
        "enable_i18n": [True, False],
    }
    default_options = {
        "devtools": False,
        "enable_i18n": True,
    }
    
    def set_version(self):
        if not self.version:
            self.version = "5.6.0-beta.1"

    @property
    def _i18n_options(self):
        return self.conf.get("user.i18n:options", default = {"extract": True, "build": True}, check_type = dict)

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

    def export_sources(self):
        copy(self, "*", os.path.join(self.recipe_folder, "plugins"), os.path.join(self.export_sources_folder, "plugins"))
        copy(self, "*", os.path.join(self.recipe_folder, "resources"), os.path.join(self.export_sources_folder, "resources"), excludes = "*.mo")
        copy(self, "*", os.path.join(self.recipe_folder, "tests"), os.path.join(self.export_sources_folder, "tests"))
        copy(self, "*", os.path.join(self.recipe_folder, "UM"), os.path.join(self.export_sources_folder, "UM"))
        copy(self, "requirements.txt", self.recipe_folder, self.export_sources_folder)
        copy(self, "requirements-dev.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type = str):
            del self.options.enable_i18n

    def configure(self):
        self.options["pyarcus"].shared = True
        self.options["cpython"].shared = True

    def validate(self):
        if self.version:
            if Version(self.version) <= Version("4"):
                raise ConanInvalidConfiguration("Only versions 5+ are support")

    def requirements(self):
        self.requires("pyarcus/5.3.0")
        self.requires("cpython/3.10.4")

    def build_requirements(self):
        if self.options.get_safe("enable_i18n", False):
            self.tool_requires("gettext/0.21@ultimaker/testing", force_host_context = True)

    def generate(self):
        vr = VirtualRunEnv(self)
        vr.generate()

        if self.options.get_safe("enable_i18n", False) and self._i18n_options["extract"]:
            vb = VirtualBuildEnv(self)
            vb.generate()

            # FIXME: once m4, autoconf, automake are Conan V2 ready use self.win_bash and add gettext as base tool_requirement
            cpp_info = self.dependencies["gettext"].cpp_info
            pot = self.python_requires["translationextractor"].module.ExtractTranslations(self, cpp_info.bindirs[0])
            pot.generate()

    def build(self):
        if self.options.get_safe("enable_i18n", False) and self._i18n_options["build"]:
            # FIXME: once m4, autoconf, automake are Conan V2 ready use self.win_bash and add gettext as base tool_requirement
            for po_file in self.source_path.joinpath("resources", "i18n").glob("**/*.po"):
                mo_file = Path(self.build_folder, po_file.with_suffix('.mo').relative_to(self.source_path))
                mo_file = mo_file.parent.joinpath("LC_MESSAGES", mo_file.name)
                mkdir(self, str(unix_path(self, Path(mo_file).parent)))
                cpp_info = self.dependencies["gettext"].cpp_info
                self.run(f"{cpp_info.bindirs[0]}/msgfmt {po_file} -o {mo_file} -f", env="conanbuild", ignore_errors=True)

    def layout(self):
        self.folders.source = "."
        self.folders.build = "venv"
        self.folders.generators = os.path.join(self.folders.build, "conan")

        self.cpp.package.libdirs = [os.path.join("site-packages", "UM")]
        self.cpp.package.resdirs = ["resources", "plugins", "pip_requirements"]  # Note: pip_requirements should be the last item in the list

    def package(self):
        copy(self, "*", src = os.path.join(self.source_folder, "UM"), dst = os.path.join(self.package_folder, self.cpp.package.libdirs[0]))
        copy(self, "*", src = os.path.join(self.source_folder, "resources"), dst = os.path.join(self.package_folder, self.cpp.package.resdirs[0]))
        copy(self, "*.mo", src = os.path.join(self.build_folder, "resources"), dst = os.path.join(self.package_folder, self.cpp.package.resdirs[0]))
        copy(self, "*", src = os.path.join(self.source_folder, "plugins"), dst = os.path.join(self.package_folder, self.cpp.package.resdirs[1]))
        copy(self, "requirement*.txt", src = self.source_folder, dst = os.path.join(self.package_folder, self.cpp.package.resdirs[-1]))

    def package_info(self):
        self.user_info.pip_requirements = "requirements.txt"
        self.user_info.pip_requirements_build = "requirements-dev.txt"

        if self.in_local_cache:
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "site-packages"))
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "plugins"))
        else:
            self.runenv_info.append_path("PYTHONPATH", self.source_folder)
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.source_folder, "plugins"))

    def package_id(self):
        self.info.clear()

        del self.info.options.devtools

