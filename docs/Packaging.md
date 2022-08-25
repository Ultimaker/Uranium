
# Packaging

*Creating a new **Uranium Conan** package* <br>
*so it can be used in **Cura** and **Uranium**.*

<br>

Run the following

```shell
conan create .                              \
    uranium/<version>@<username>/<channel>  \
    --build=missing                         \
    --update
```

<br>

This package will be stored in the local Conan cache.

`~/.conan/data` or `C:\Users\username\.conan\data`

<br>

It can be used in downstream projects, such as **Cura** and **Uranium** by <br>
adding it as a requirement in the `conanfile.py` or in `conandata.yml`.

*Make sure that the used `<version>` is present <br>
in the `conandata.yml` in the Uranium root.*

<br>

You can also specify the override at the commandline, to use the <br>
newly created package, when you execute the install command <br>
in the root of the consuming project.


```shell
conan install .     \
    -build=missing  \ 
    --update        \
    --require-override=uranium/<version>@<username>/<channel>
```

<br>