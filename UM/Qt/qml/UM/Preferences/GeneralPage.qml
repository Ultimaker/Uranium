// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.1 as UM

PreferencesPage
{
    title: "General";

    function reset() {
        UM.Preferences.resetPreference("general/language")
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
                ListElement { text: "English"; code: "en_US" }
            }

            currentIndex:
            {
                var code = UM.Preferences.getValue("general/language");
                var index = 0;
                for(var i = 0; i < languageList.count; ++i)
                {
                    if(model.get(i).code == code)
                    {
                        index = i;
                        break;
                    }
                }
                return index;
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
    }
}
