Translation Guide
=================

This page describes the procedures and methods related to translations for Uranium & Cura.

Developers mark strings as translatable. These strings are extracted from the source files and copied to one or more translation files. These translation files are then sent out for translation. Once translated, these files are compiled into a translation catalog. This translation catalog is then used to look up the translated strings.

The first paragraph in this document ("Mark strings as translatable in Python") is important for all developers that work on Cura. The rest of the document is for developers that extract (or test) the translations. 

Mark strings as translatable in Python
--------------------------------------

Import either Cura's or Uraniums i18n Catalog (depending whether you're working in Uranium or Cura..). Assign the appropriate catalog to a variable named 'i18n_catalog'. 
```
from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("cura")
```
Each string in Uranium should be provided with a context. These contexts and the strings are marked up using "semantic markup", a system based on KDE's [semantic markup]. This format is intended to provide a standardised way of providing additional
information about the usage and the meaning of strings. [semantic markup]:
https://techbase.kde.org/Development/Tutorials/Localization/i18n_Semantics

###Use named arguments for string formatting
When you perform string formatting with multiple arguments, you need to use named arguments instead of positional arguments. 

~~return self._i18n_catalog.i18nc("@info", "%.1f x %.1f x %.1f mm") % (self._scene_boundingbox.width.item(), self._scene_boundingbox.depth.item(), self._scene_boundingbox.height.item())~~
```
return self._i18n_catalog.i18nc("@info", "%(width).1f x %(depth).1f x %(height).1f mm") % {'width' : self._scene_boundingbox.width.item(), 'depth': self._scene_boundingbox.depth.item(), 'height' : self._scene_boundingbox.height.item()}
```

###String Placeholders and Semantic Tags
String contents can have placeholders where certain other elements should be
inserted. For example, these are used to insert file names when displaying
messages about file saving. These placeholders are use a format with a number
surrounded by curly brackets ({}). Additionally, these placeholders can be
surrounded by semantic tags. Semantic tags indicate the function of a
placeholder.

Currently, the following two semantic tags are available:
* <filename></filename> Used to denote a filename.
* <message></message> Used to denote an error message.

###Add extra context-markers for alt-key accelerated menu-items
In the menubar we use alt-key accelerators. (With alt + E the Edit menu opens; after this with alt + S you activate Delete Selection.) These strings need extra context so the translator knows in which group the chosen accelerated letter needs to be unique. We currently have the following added contact markers: 
```
menubar:toplevel (→ all toplevel menu-items)
menubar:file (→ all items that fall under the 'file' toplevel menu-item)
menubar:edit
menubar:printer
menubar:profile
menubar:settings
menubar:help
```
Use the following format to add a context-marker to a menu-item: 
```
i18n_catalog.i18nc("@action:inmenu menubar:edit","&Group Objects")
```
You also add these context markers when there is only one item in the menu or when the menu-item doesn't use an alt-key accelerator (yet). If you change the string of a toplevel item; you obviously also change the context-markers of the underlying menu-items. More info on alt-key accelerators here: http://doc.qt.io/qt-5/linguist-translators.html#changing-keyboard-accelerators


Mark a string as translatable in QML
------------------------------------

Insert the i18n catalog object into your qml file.  Obviously the name needs to be cura or uranium, whether you're working in Cura or Uranium.
```
UM.I18nCatalog{id: i18n_catalog; name:"cura"}
```
For convenience we name the id 'i18n_catalog'. Everything else works exactly the same as in python: 
```
i18n_catalog.i18nc("@action:button", "Back");
```

Extract the messages
--------------------

The following steps are pretty much the same for both Cura and Uranium, but have to be performed for both separately. The only difference is that in Cura you have to open CmakeLists.txt and make sure that URANIUM_SCRIPTS_DIR is set to the correct folder (the folder in Uranium that contains the scripts). Use the terminal to create the buildfiles in a new build folder in the source-directory: 
```
mkdir build
cd build
cmake ..
cd ..
```
`make` commands can now be executed from the project root. Now build the build-target [extract-messages] (with the terminal; when your still in the build directory). (If it starts wining that it can't find some directory; fix it, throw away the build folder and create the build-files again.)
```
make extract-messages
```

It has created a freshly extracted POT file. 
Don't worry if you're not a 100% sure that the files are correct; we are going to perform a very telling test later in the process. Having said that; you do need to check the following: The script tends to break on certain characters in the JSON files. Review these files by checking if the last translatable string in the json file is also the last item in the POT file. 

Theory on translation files
---------------------------
First some theory on the magic translation files. These are the different files: 

| Short Name    | Long Name                       | File-extension  | Description                       |
| ------------- | ------------------------------- |---------------- |---------------------------------- |
| POT file      | Portable Template Object file   | .pot            | template for the PO files         |
| PO file       | Portable Object file            | .po             | contains the actual translations  |
| MO file       | Machine Object file             | .mo             | binary code; used by Cura         |

As said before [extract-messages] creates a POT file. The POT file is a template for the .PO files.The PO files are based on the POT file. And the PO files are compiled into MO files. 

Creating the PO files
---------------------

[extract-messages] Has already created the PO files it can automatically create (English and x-test). The other PO files are created by merging the old PO file with the new POT file. If you don't merge them; you have to get completely new translations with every new release. An added bonus is that translations that are no longer used don't get thrown away, but are commented out and placed in the bottom of the page for later use. Use the terminal to create the new PO files:
```
make i18n-create-po
```
For a specific language code use:
```
make i18n-create-po-<code>
```
msgmerge Does such a great job that I usually just rewrite the old PO file. 
```
make i18n-update-po
```
Same here for a specific language:
```
make i18n-update-po-<code>
```

Creating the MO files & testing
-------------------------------
In the building process; the MO files are automatically created. So you only manually create the MO files that you want to test. A great example is x-test. The PO files for x-test are automatically created by [extract-messages]. It is basically an English translation with two X's before and after each string. You use it to test whether all strings are being properly translated.  

The directory of the language (x-test is this example) must contain a special directory called `LC_MESSAGES`. This directory is created automatically. Create the MO file with the terminal (project root): 
```
make i18n-create-mo
```
Or for your language:
```
make i18n-create-mo-<code>
```
Setting the environment variable doesn't function. So for now you need to edit the language default in: Uranium/UM/i18n.py
~~def __init__(self, name = None, language = "default"):~~
```
def __init__(self, name = None, language = "x-test"):
```
Carefully test whether ALL strings are being properly translated, before you send the PO files to the translators. You can test this by looking if all strings have 2 X's around them. 

Finally
-------
Send both the POT files and the PO files to the translators. Translators like to use PO editors. These are programs that allow them to translate one string at-a-time without having to look into the actual code. These programs tend to turn multi-line strings into single line strings. This is not a problem for Cura, just leave it as it is. 
