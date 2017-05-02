# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import gettext
from typing import Any, Dict

from UM.Resources import Resources

##  Wraps a gettext translation catalog for simplified use.
#
#   This class wraps a gettext translation catalog to simplify its use.
#   It will load the translation catalog from Resources' i18nLocation
#   and allows specifying which language to load.
#
#   To use this class, create an instance of it with the name of the catalog
#   to load. Then call `i18n` or `i18nc` on the instance to perform a look
#   up in the catalog.
#
#   Standard Contexts and Translation Tags
#   --------------------------------------
#
#   The translation system relies upon a set of standard contexts and HTML-like
#   translation tags. Please see the [translation guide](docs/translations.md)
#   for details.
#
class i18nCatalog: # [CodeStyle: Ultimaker code style requires classes to start with a upper case. But i18n is lower case by convention.] pylint: disable=invalid-name
    ##  Creates a new catalogue.
    #
    #   \param name The name of the catalog to load.
    #   \param language The language to load. Valid values are language codes or
    #   "default". When "default" is specified, the language to load will be
    #   determined based on the system"s language settings.
    #
    #   \note When `language` is `default`, the language to load can be
    #   overridden using the "LANGUAGE" environment variable.
    def __init__(self, name: str = None, language: str = "default") -> None: #pylint: disable=bad-whitespace
        self.__name = name
        self.__language = language
        self.__translation = None   # type: Optional[gettext.NullTranslations]

        self._update() #Load the actual translation document now that the language is set.

    ##  Whether the translated texts are loaded into this catalogue.
    #
    #   If there are translated texts, it is safe to request the text with the
    #   ``gettext`` method and so on.
    #
    #   \return ``True`` if texts are loaded into this catalogue, or ``False``
    #   if they aren't.
    def hasTranslationLoaded(self) -> bool:
        return self.__translation is not None

    ##  Mark a string as translateable.
    #
    #   \param text The string to mark as translatable
    #   \param args Formatting arguments. These will replace formatting elements
    #   in the translated string. See python ``str.format()``.
    #   \return The translated text or the untranslated text if no translation
    #   was found.
    def i18n(self, text: str, *args: Any) -> str:

        if self.__require_update:
            self._update()

        translated = text  # Default to hard-coded text if no translation catalogue is loaded.
        if self.hasTranslationLoaded():
            translated = self.__translation.gettext(text)

        if args:
            translated = translated.format(*args)  # Positional arguments are replaced in the (translated) text.
        return self._replaceTags(translated)  # Also replace the global keys.

    ##  Mark a string as translatable and provide a context for translators.
    #
    #   \param context The context of the string, i.e. something that explains
    #   the use of the text.
    #   \param text The text to mark translatable.
    #   \param args Formatting arguments. These will replace formatting elements
    #   in the translated string. See python ``str.format()``.
    #   \return The translated text or the untranslated text if it was not found
    #   in this catalog.
    def i18nc(self, context: str, text: str, *args: Any) -> str:
        if self.__require_update:
            self._update()

        translated = text  # Default to hard-coded text if no translation catalogue is loaded.
        if self.hasTranslationLoaded():
            message_with_context = "{0}\x04{1}".format(context, text)  # \x04 is "end of transmission" byte, indicating to gettext that they are two different texts.
            message = self.__translation.gettext(message_with_context)
            if message != message_with_context:
                translated = message

        if args:
            translated = translated.format(*args)  # Positional arguments are replaced in the (translated) text.
        return self._replaceTags(translated)  # Also replace the global keys.

    ##  Mark a string as translatable with plural forms.
    #
    #   \param single The singular form of the string.
    #   \param multiple The plural form of the string.
    #   \param counter The value that determines whether the singular or plural
    #   form should be used.
    #   \param args Formatting arguments. These will replace formatting elements
    #   in the translated string. See python ``str.format()``.
    #   \return The translated string, or the untranslated text if no
    #   translation could be found. Note that the fallback simply checks if
    #   counter is greater than one and if so, returns the plural form.
    #
    #   \note For languages other than English, more than one plural form might
    #   exist. The counter is at all times used to determine what form to use,
    #   with the language files specifying what plural forms are available.
    #   Additionally, counter is passed as first argument to format the string.
    def i18np(self, single: str, multiple: str, counter: int, *args: Any) -> str:
        if self.__require_update:
            self._update()

        translated = multiple if counter != 1 else single  # Default to hard-coded texts if no translation catalogue is loaded.
        if self.hasTranslationLoaded():
            translated = self.__translation.ngettext(single, multiple, counter)

        translated = translated.format(counter, args)  # Positional arguments are replaced in the (translated) text, but this time the counter is treated as the first argument.
        return self._replaceTags(translated)  # Also replace the global keys.

    ##  Mark a string as translatable with plural forms and a context for
    #   translators.
    #
    #   \param context The context of this string.
    #   \param single The singular form of the string.
    #   \param multiple The plural form of the string.
    #   \param counter The value that determines whether the singular or plural
    #   form should be used.
    #   \param args Formatting arguments. These will replace formatting elements
    #   in the translated string. See python ``str.format()``.
    #   \return The translated string, or the untranslated text if no
    #   translation could be found. Note that the fallback simply checks if
    #   counter is greater than one and if so returns the plural form.
    #
    #   \note For languages other than English, more than one plural form might
    #   exist. The counter is at all times used to determine what form to use,
    #   with the language files specifying what plural forms are available.
    #   Additionally, counter is passed as first argument to format the string.
    def i18ncp(self, context: str, single: str, multiple: str, counter: int, *args: Any) -> str:
        if self.__require_update:
            self._update()

        translated = multiple if counter != 1 else single  # Default to hard-coded texts if no translation catalogue is loaded.
        if self.hasTranslationLoaded():
            message_with_context = "{0}\x04{1}".format(context, single)  # \x04 is "end of transmission" byte, indicating to gettext that they are two different texts.
            message = self.__translation.ngettext(message_with_context, multiple, counter)

            if message != message_with_context:
                translated = message

        translated = translated.format(counter, args)
        return self._replaceTags(translated)

    ##  Replace formatting tags in the string with globally-defined replacement
    #   values.
    #
    #   Which tags are replaced can be defined using the ``setTagReplacements``
    #   method.
    #
    #   \param string The text to replace tags in.
    #   \return The text with its tags replaced.
    def _replaceTags(self, string: str) -> str:
        output = string
        for key, value in self.__tag_replacements.items():
            source_open = "<{0}>".format(key)
            source_close = "</{0}>".format(key)

            if value:
                dest_open = "<{0}>".format(value)
                dest_close = "</{0}>".format(value)
            else:
                dest_open = ""
                dest_close = ""

            output = output.replace(source_open, dest_open).replace(source_close, dest_close)

        return output

    ##  Fill the catalogue by loading the translated texts from file (again).
    def _update(self) -> None:
        if not self.__application:
            self.__require_update = True
            return

        if not self.__name:
            self.__name = self.__application.getApplicationName()
        if self.__language == "default":
            self.__language = self.__application.getApplicationLanguage()

        # Ask gettext for all the translations in the .mo files.
        for path in Resources.getAllPathsForType(Resources.i18n):
            if gettext.find(self.__name, path, languages = [self.__language]):
                self.__translation = gettext.translation(self.__name, path, languages = [self.__language])

        self.__require_update = False

    ##  Change the global tags that are replaced in every internationalised
    #   string.
    #
    #   If a text contains something of the form ``<key>`` or ``</key>``, then
    #   the word ``key`` will get replaced by whatever is in this dictionary at
    #   the specified key.
    #
    #   \param replacements A dictionary of strings to strings, indicating which
    #   words between tags should get replaced.
    @classmethod
    def setTagReplacements(cls, replacements: Dict[str, str]) -> None:
        cls.__tag_replacements = replacements

    ##  Set the ``Application`` instance to request the language and application
    #   name from.
    #
    #   \param application The ``Application`` instance of the application that
    #   is running.
    @classmethod
    def setApplication(cls, application):
        cls.__application = application

    @classmethod
    def setApplicationName(cls, applicationName: str) -> None:
        cls.__name = applicationName
        cls.__require_update = True

    @classmethod
    def setLanguage(cls, language: str) -> None:
        cls.__language = language
        cls.__require_update = True

    # Default replacements discards all tags
    __tag_replacements = {
        "filename": None,
        "message": None
    }   # type: Dict[str, str]
    __application = None
