from UM.Resources import Resources
from UM.Preferences import Preferences

import gettext
import os

##  Wraps a gettext translation catalog for simplified use.
#
#   This class wraps a gettext translation catalog to simplify its use.
#   It will load the translation catalog from Resources' i18nLocation
#   and allows specifying which language to load.
#
#   To use this class, create an instance of it with the name of the catalog
#   to load. Then call `i18n` or `i18nc` on the instance to perform a look
#   up in the catalog.
class i18nCatalog:
    ##  Constructor.
    #
    #   \param name The name of the catalog to load.
    #   \param language The language to load. Valid values are language codes or
    #   "default". When "default" is specified, the language to load will be
    #   determined based on the system"s language settings.
    #
    #   \note When `language` is `default`, the language to load can be overridden
    #   using the "LANGUAGE" environment variable.
    def __init__(self, name, language = "default"):
        languages = []
        if language == "default":
            envlang = os.getenv("LANGUAGE")
            if envlang:
                languages.append(envlang)
            else:
                preflang = Preferences.getInstance().getValue("general/language")
                if preflang:
                    languages.append(preflang)
        else:
            languages.append(language)

        for path in Resources.getLocation(Resources.i18nLocation):
            if gettext.find(name, path, languages = languages):
                self.__translation = gettext.translation(name, path, languages=languages)
                break
        else:
            self.__translation = None

    ##  Mark a string as translatable
    #
    #   \param text The string to mark as translatable
    def i18n(self, text):
        if self.__translation:
            return self.__translation.gettext(text)

        return text

    ##  Mark a string as translatable, provide a context.
    #
    #   \param context The context of the string, i.e. something that explains the use of the text.
    #   \param text The text to mark translatable.
    #
    #   \return The translated text or the untranslated text if it was not found in this catalog.
    def i18nc(self, context, text):
        if self.__translation:
            message_with_context = "{0}\x04{1}".format(context, text)
            translated = self.__translation.gettext(message_with_context)
            if translated == message_with_context:
                return text
            else:
                return translated

        return text

    #TODO: Add support for plural formats
