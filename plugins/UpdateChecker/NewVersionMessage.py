# Copyright (c) 2021 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from UM import i18nCatalog
from UM.Application import Application
from UM.Message import Message
from UM.Version import Version

from .AnnotatedUpdateMessage import AnnotatedUpdateMessage

I18N_CATALOG = i18nCatalog("uranium")


class NewVersionMessage(AnnotatedUpdateMessage):
    def __init__(self, application_display_name: str, newest_version: Version) -> None:
        super().__init__(
            title = I18N_CATALOG.i18nc("@info:status",
                                        "{application_name} {version_number} is available!").format(
                                        application_name = application_display_name,
                                        version_number = newest_version),
            text = I18N_CATALOG.i18nc("@info:status",
                                         "{application_name} {version_number} provides a better and more reliable printing experience.").format(
                                         application_name = application_display_name,
                                         version_number = newest_version))

        self.change_log_url = Application.getInstance().change_log_url

        self.addAction("download", I18N_CATALOG.i18nc("@action:button", "Download"), "[no_icon]", "[no_description]")

        self.addAction("new_features", I18N_CATALOG.i18nc("@action:button", "Learn more"), "[no_icon]",
                          "[no_description]",
                          button_style = Message.ActionButtonStyle.LINK,
                          button_align = Message.ActionButtonAlignment.ALIGN_LEFT)
