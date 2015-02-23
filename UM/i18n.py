from UM.Resources import Resources

import gettext
import os

class i18nCatalog:
    def __init__(self, name, language = 'default'):
        languages = []
        if language == 'default':
            preflang = None #TODO: Read from preferences

            if not preflang:
                envlang = os.getenv('LANGUAGE')
                if envlang:
                    languages.append(envlang)
            else:
                languages.append(preflang)
        else:
            languages.append(language)

        try:
            self.__translation = gettext.translation(name, Resources.getLocation(Resources.i18nLocation), languages=languages)
        except FileNotFoundError:
            self.__translation = None

    def getInfo(self):
        if not self.__translation:
            return {}

        return self.__translation.info()

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
            return self.__translation.gettext("{0}\x04{1}".format(context, text))

        return text

    #TODO: Add support for plural formats
