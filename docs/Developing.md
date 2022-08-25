## Developing Uranium In Editable Mode

You can use your local development repository downsteam by adding it as an editable mode package.
This means you can test this in a consuming project without creating a new package for this project every time.

```bash
    conan editable add . uranium/<version>@<username>/<channel>
```

Then in your downsteam projects (Cura) root directory override the package with your editable mode package.  

```shell
conan install . -build=missing --update --require-override=uranium/<version>@<username>/<channel>
```
