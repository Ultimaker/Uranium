Translation Guide
=================

This page describes the procedures and method related to translations for
Uranium.

Developers mark strings as translatable. These strings are extracted from the
source files and copied to one or more translation files. These translation
files are then sent out for translation. Once translated, these files are
compiled into a translation catalog. This translation catalog is then used to
look up the translated strings.


Semantic Markup
---------------

Each string in Uranium should have a context. These contexts and the strings
are marked up using "semantic markup", a system based on KDE's [semantic markup].
This format is intended to provide a standardised way of providing additional
information about the usage and the meaning of strings.

[semantic markup]:
https://techbase.kde.org/Development/Tutorials/Localization/i18n_Semantics

Semantic Contexts
-----------------

Each context follows a simple format, using an "@" followed by a name to denote
a role, optionally followed by a ":" and a name to denote a subcue. Finally, there
is optional disambiguation text that follows the role and subcue. Please see
[KDE's list of Context markers][kde] for the complete list of supported context
markers and their uses.

[kde]: https://techbase.kde.org/Development/Tutorials/Localization/i18n_Semantics#Context_Markers

String Placeholders and Semantic Tags
-------------------------------------

String contents can have placeholders where certain other elements should be
inserted. For example, these are used to insert file names when displaying
messages about file saving. These placeholders are use a format with a number
surrounded by curly brackets ({}). Additionally, these placeholders can be
surrounded by semantic tags. Semantic tags indicate the function of a
placeholder.

Currently, the following two semantic tags are available:

* <filename></filename> Used to denote a filename.
* <message></message> Used to denote an error message.
