
# Developing Uranium <br> In Editable Mode

<br>

[![Button Building]][Building]   
[![Button Packaging]][Packaging]

<br>
<br>

You can use your local development repository downsteam <br>
by adding it as an editable mode package, which also means <br>
that you can test it in a consuming project without creating <br>
a new package for this project every time.


```shell
conan editable add . \
    uranium/<version>@<username>/<channel>
```

<br>

Then in your downsteam project's ( Cura ) root directory <br>
override the package with your editable mode package.  

```shell
conan install .     \
    -build=missing  \
    --update        \
    --require-override=uranium/<version>@<username>/<channel>
```

<br>


<!----------------------------------------------------------------------------->

[Packaging]: Packaging.md
[Building]: Building.md


<!---------------------------------[ Buttons ]--------------------------------->

[Button Packaging]: https://img.shields.io/badge/Packaging-458cb5?style=for-the-badge&logoColor=white&logo=GitLFS
[Button Building]: https://img.shields.io/badge/Building-629944?style=for-the-badge&logoColor=white&logo=CurseForge
