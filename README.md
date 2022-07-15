# Uranium

<p align="center">
    <a href="https://github.com/Ultimaker/Uranium/actions/workflows/unit-test.yml" alt="Unit Tests">
        <img src="https://github.com/Ultimaker/Uranium/actions/workflows/unit-test.yml/badge.svg" /></a>
    <a href="https://github.com/Ultimaker/Uranium/actions/workflows/conan-package.yml" alt="Unit Tests">
        <img src="https://github.com/Ultimaker/Uranium/actions/workflows/conan-package.yml/badge.svg" /></a>
    <a href="https://github.com/Ultimaker/Uranium/issues" alt="Open Issues">
        <img src="https://img.shields.io/github/issues/ultimaker/cura" /></a>
    <a href="https://github.com/Ultimaker/Uranium/issues?q=is%3Aissue+is%3Aclosed" alt="Closed Issues">
        <img src="https://img.shields.io/github/issues-closed/ultimaker/uranium?color=g" /></a>
    <a href="https://github.com/Ultimaker/Uranium/pulls" alt="Pull Requests">
        <img src="https://img.shields.io/github/issues-pr/ultimaker/Uranium" /></a>
    <a href="https://github.com/Ultimaker/Uranium/graphs/contributors" alt="Contributors">
        <img src="https://img.shields.io/github/contributors/ultimaker/uranium" /></a>
    <a href="https://github.com/Ultimaker/Uranium" alt="Repo Size">
        <img src="https://img.shields.io/github/repo-size/ultimaker/uranium?style=flat" /></a>
    <a href="https://github.com/Ultimaker/Uranium/blob/master/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/ultimaker/uranium?style=flat" /></a>
</p>


Uranium is a Python framework for building 3D printing related applications.

## License

![License](https://img.shields.io/github/license/ultimaker/uranium?style=flat)  
Uranium is released under terms of the LGPLv3 License. Terms of the license can be found in the LICENSE file. Or at
http://www.gnu.org/licenses/lgpl.html

> But in general it boils down to:  
> **You need to share the source of any Uranium modifications if you make an application with Uranium.**

## How to set up a development environment

> **Note:**  
> We are currently in the process of switch our builds and pipelines to an approach which uses [Conan](https://conan.io/)
> and pip to manage our dependencies, which are stored on our JFrog Artifactory server and in the pypi.org.
> At the moment not everything is fully ported yet, so bare with us.

If you want to develop Cura with Uranium see the Cura Wiki: [Running Cura from source](https://github.com/Ultimaker/Cura/wiki/Running-Cura-from-Source)

If you have never used [Conan](https://conan.io/) read their [documentation](https://docs.conan.io/en/latest/index.html)
which is quite extensive and well maintained. Conan is a Python program and can be installed using pip

```bash
pip install conan --upgrade
conan config install https://github.com/ultimaker/conan-config.git
conan profile new default --detect
```

**Community developers would have to remove the Conan `cura` repository because that one requires credentials.**
```bash
conan remote remove cura
```

### Install Uranium dependencies

```bash
conan install . --build=missing --profile=default -o uranium:devtools=True -g VirtualPythonEnv
```

This will create a Virtual Python Environment and install all the dependencies. You can then activate and run the unittests.

```bash
# For Linux/MacOS
source venv/bin/activate
cd tests
pytest
```

```powershell
# For Windows (Powershell)
.\venv\Scripts\activate.ps1
cd tests
pytests
```

## Creating a new Uranium Conan package

To create a new Uranium Conan package such that it can be used in Cura, run the following command:

```shell
conan create . uranium/<version>@<username>/<channel> --build=missing --update
```

This package will be stored in the local Conan cache (`~/.conan/data` or `C:\Users\username\.conan\data` ) and can be used in downstream
projects, such as Cura, by adding it as a requirement in the `conanfile.py` or in `conandata.yml` if that project is set up
in such a way. You can also specify the override at the commandline, to use the newly created package, when you execute the `conan install`
command in the root of the consuming project, with:

```shell
conan install . -build=missing --update --require-override=uranium/<version>@<username>/<channel>
```
