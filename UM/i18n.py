import gettext

##  Mark a string as translatable
#
#   \param text The string to mark as translatable
def i18n(text):
    return text

##  Mark a string as translatable, provide a context.
#
#   \param context The context of the string, i.e. something that explains the use of the text.
#   \param text The text to mark translatable.
def i18nc(context, text):
    return text
