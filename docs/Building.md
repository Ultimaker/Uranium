
# Building

<br>

> We are currently in the process of switch our builds <br>
> and pipelines to an approach which uses **[Conan]** and <br>
> pip to manage our dependencies, which are stored <br>
> on our **JFrog Artifactory** server and in the pypi.org.
>
> *Not everything has been fully ported yet, so bare with us.*


<br>
<br>

## Related

If you want to develop Cura with Uranium see the **[Cura Wiki][Cura From Source]**.

**[Conan]** is a Python program and can be installed using pip. <br>
If you have never used it read their **[Documentation][Conan Docs]** which <br>is quite extensive and well maintained.


<br>
<br>

## Configuring Conan

<br>

```shell
pip install conan --upgrade
conan config install https://github.com/ultimaker/conan-config.git
conan profile new default --detect --force
```

<br>

Community developers would have to remove the <br>
Conan cura repository because it requires credentials. 

Ultimaker developers need to request an <br>
account for our JFrog Artifactory server at IT.

```shell
conan remote remove cura
```

<br>
<br>

## Clone Uranium

<br>

```shell
git clone https://github.com/Ultimaker/Uranium.git
cd Uranium
```

<br>
<br>

## Environment Initialization

*Initializing the Virtual Python Development Environment.*

<br>

Install the dependencies for the development environment and initialize <br>
a virtual Python environment. Execute the following command in the root <br>
directory of the Cura repository.

```shell
conan install .             \
    --build=missing         \
    -o cura:devtools=True   \
    -g VirtualPythonEnv
```

<br>
<br>

## Running Tests

<br>

### Linux / MacOS

```shell
source venv/bin/activate
cd tests
pytest
```

<br>

### Windows

```powershell
.\venv\Scripts\activate.ps1
cd tests
pytests
```

<br>


<!----------------------------------------------------------------------------->

[Cura From Source]: https://github.com/Ultimaker/Cura/wiki/Running-Cura-from-Source
[Conan Docs]: https://docs.conan.io/en/latest/index.html
[Conan]: https://conan.io/
