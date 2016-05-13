// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.1 as UM

PreferencesPage
{
    title: "General";

    function reset() {
        UM.Preferences.resetPreference("general/language")
        UM.Preferences.resetPreference("info/automatic_update_check")
        checkUpdatesCheckbox.checked = boolCheck(UM.Preferences.getValue("info/automatic_update_check"))
    }

    Column
    {
        Label
        {
            id: languageLabel
            text: "Language"
        }

        ComboBox
        {
            id: languageComboBox
            model: ListModel {
                id: languageList
                ListElement { text: "English"; code: "en" }
            }

            currentIndex:
            {
                var code = UM.Preferences.getValue("general/language");
                for(var i = 0; i < languageList.count; ++i)
                {
                    if(model.get(i).code == code)
                    {
                        return i
                    }
                }
            }

            onActivated: UM.Preferences.setValue("general/language", model.get(index).code)
        }

        Label
        {
            id: languageCaption;
            text: "You will need to restart the application for language changes to have effect."
            wrapMode: Text.WordWrap
            font.italic: true
        }

        UM.TooltipArea {
            width: childrenRect.width
            height: childrenRect.height
            text: catalog.i18nc("@info:tooltip","Should the program check for updates when it is started?")

            CheckBox
            {
                id: checkUpdatesCheckbox
                text: catalog.i18nc("@option:check","Check for updates on start")
                checked: boolCheck(UM.Preferences.getValue("info/automatic_update_check"))
                onCheckedChanged: UM.Preferences.setValue("info/automatic_update_check", checked)
            }
        }
    }
}
