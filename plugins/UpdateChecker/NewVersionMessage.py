from UM import i18nCatalog
from UM.Message import Message
from UM.Version import Version

I18N_CATALOG = i18nCatalog("uranium")


class NewVersionMessage(Message):
    def __init__(self, application_display_name: str, newest_version: Version):
        super().__init__(
            text = I18N_CATALOG.i18nc("@info:status",
                                        "{application_name} {version_number} is available!".format(
                                        application_name=application_display_name,
                                        version_number=newest_version)),
            title = I18N_CATALOG.i18nc("@info:status",
                                         "{application_name} {version_number} provides a better and more reliable printing experience.".format(
                                         application_name = application_display_name,
                                         version_number = newest_version)))

        self.addAction("download", I18N_CATALOG.i18nc("@action:button", "Download"), "[no_icon]", "[no_description]")

        self.addAction("new_features", I18N_CATALOG.i18nc("@action:button", "Learn more"), "[no_icon]",
                          "[no_description]",
                          button_style=Message.ActionButtonStyle.LINK,
                          button_align=Message.ActionButtonAlignment.ALIGN_LEFT)