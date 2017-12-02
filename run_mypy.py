#!env python
import os
import sys
import subprocess

# A quick Python implementation of unix 'where' command.
def where(exeName):
    searchPath = os.getenv("PATH")
    paths = searchPath.split(";" if sys.platform == "win32" else ":")
    for path in paths:
        candidatePath = os.path.join(path, exeName)
        if os.path.exists(candidatePath):
            return candidatePath
    return None

def main():
    if sys.platform == "win32":
        os.putenv("MYPYPATH", r".;.\stubs")
    else:
        os.putenv("MYPYPATH", r".:./stubs")

    # Mypy really needs to be run via its Python script otherwise it can't find its data files.
    mypyExe = where("mypy.bat" if sys.platform == "win32" else "mypy")
    mypyModule = os.path.join(os.path.dirname(mypyExe), "mypy")

    result = subprocess.run([sys.executable, mypyModule, "-p", "UM"])
    if result.returncode != 0:
        print("Type checking failed.")
    else:
        print("""

    Done checking. All is good.
    """)

    return 0
sys.exit(main())
