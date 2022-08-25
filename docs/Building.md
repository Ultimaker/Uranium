## How To Build

> **Note:**  
> We are currently in the process of switch our builds and pipelines to an approach which uses [Conan](https://conan.io/)
> and pip to manage our dependencies, which are stored on our JFrog Artifactory server and in the pypi.org.
> At the moment not everything is fully ported yet, so bare with us.

If you want to develop Cura with Uranium see the Cura Wiki: [Running Cura from source](https://github.com/Ultimaker/Cura/wiki/Running-Cura-from-Source)

If you have never used [Conan](https://conan.io/) read their [documentation](https://docs.conan.io/en/latest/index.html)
which is quite extensive and well maintained. Conan is a Python program and can be installed using pip

### 1. Configure Conan

```bash
pip install conan --upgrade
conan config install https://github.com/ultimaker/conan-config.git
conan profile new default --detect --force
```

Community developers would have to remove the Conan cura repository because it requires credentials. 

Ultimaker developers need to request an account for our JFrog Artifactory server at IT
```bash
conan remote remove cura
```

### 2. Clone Uranium
```bash
git clone https://github.com/Ultimaker/Uranium.git
cd Uranium
```

### 3. Initialize the Virtual Python Development Environment

Install the dependencies for the development environment and initialize a virtual Python environment. Execute the
following command in the root directory of the Cura repository.

```bash
conan install . --build=missing -o cura:devtools=True -g VirtualPythonEnv
```

### 4. Running tests
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