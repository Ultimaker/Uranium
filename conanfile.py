import os

from pathlib import Path

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, mkdir, update_conandata
from conan.tools.microsoft import unix_path
from conan.tools.scm import Version, Git
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.7.0"


class UraniumConan(ConanFile):
    name = "uranium"
    license = "LGPL-3.0"
    author = "UltiMaker"
    url = "https://github.com/Ultimaker/uranium"
    description = "A Python framework for building Desktop applications."
    topics = ("conan", "python", "pyqt6", "qt", "3d-graphics", "3d-models", "python-framework")
    exports = "LICENSE*"
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualPythonEnv"
    package_type = "header-library"

    python_requires = "translationextractor/[>=2.2.0]"
    tool_requires = "gettext/0.22.5"

    options = {
        "i18n_extract": [True, False],
    }
    default_options = {
        "i18n_extract": False,
    }

    def set_version(self):
        if not self.version:
            self.version = self.conan_data["version"]

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

    def export(self):
        git = Git(self)
        update_conandata(self, {"version": self.version, "commit": git.get_commit()})

    def export_sources(self):
        copy(self, "*", os.path.join(self.recipe_folder, "plugins"),
             os.path.join(self.export_sources_folder, "plugins"))
        copy(self, "*", os.path.join(self.recipe_folder, "resources"),
             os.path.join(self.export_sources_folder, "resources"), excludes="*.mo")
        copy(self, "*", os.path.join(self.recipe_folder, "tests"), os.path.join(self.export_sources_folder, "tests"))
        copy(self, "*", os.path.join(self.recipe_folder, "UM"), os.path.join(self.export_sources_folder, "UM"))

    def validate(self):
        if self.options.i18n_extract and self.settings.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            raise ConanInvalidConfiguration("Unable to extract translations on Windows without Bash installed")

    def configure(self):
        self.options["pyarcus"].shared = True
        self.options["cpython"].shared = True
        if self.settings.os == "Linux":
            self.options["openssl"].shared = True

    def requirements(self):
        for req in self.conan_data["requirements"]:
            self.requires(req)
        self.requires("cpython/3.12.2")

    def generate(self):
        vr = VirtualRunEnv(self)
        vr.generate()

        if self.options.i18n_extract:
            vb = VirtualBuildEnv(self)
            vb.generate()

            pot = self.python_requires["translationextractor"].module.ExtractTranslations(self)
            pot.generate()

    def build(self):
        for po_file in Path(self.source_folder, "resources", "i18n").glob("**/*.po"):
            mo_file = Path(self.build_folder, po_file.with_suffix('.mo').relative_to(self.source_folder))
            mo_file = mo_file.parent.joinpath("LC_MESSAGES", mo_file.name)
            mkdir(self, str(unix_path(self, Path(mo_file).parent)))
            self.run(f"msgfmt {po_file} -o {mo_file} -f", env="conanbuild")

    def layout(self):
        self.folders.source = "."
        self.folders.build = "build"
        self.folders.generators = os.path.join(self.folders.build, "generators")

        self.cpp.package.libdirs = [os.path.join("site-packages", "UM")]
        self.cpp.package.resdirs = ["resources", "plugins"]

        self.layouts.source.runenv_info.prepend_path("PYTHONPATH", ".")
        self.layouts.source.runenv_info.prepend_path("PYTHONPATH", "plugins")
        self.layouts.package.runenv_info.prepend_path("PYTHONPATH", "site-packages")
        self.layouts.package.runenv_info.prepend_path("PYTHONPATH", self.cpp.package.resdirs[1])

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "UM"),
             dst=os.path.join(self.package_folder, self.cpp.package.libdirs[0]))
        copy(self, "*", src=os.path.join(self.source_folder, "resources"),
             dst=os.path.join(self.package_folder, self.cpp.package.resdirs[0]))
        copy(self, "*.mo", src=os.path.join(self.build_folder, "resources"),
             dst=os.path.join(self.package_folder, self.cpp.package.resdirs[0]))
        copy(self, "*", src=os.path.join(self.source_folder, "plugins"),
             dst=os.path.join(self.package_folder, self.cpp.package.resdirs[1]))

    def package_id(self):
        self.info.clear()

        self.info.options.rm_safe("i18n_extract")
