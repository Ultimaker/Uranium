// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.1 as UM

PreferencesPage
{
    //: General configuration page title
    title: catalog.i18nc("@title:window","General");

    function reset() {
        UM.Preferences.resetPreference("general/language")
    }

    Column
    {
        Label
        {
            id: languageLabel
            text: catalog.i18nc("@label","Language")
            UM.I18nCatalog { id: catalog; name:"uranium"}
        }

        ComboBox
        {
            id: languageComboBox
            model: ListModel {
                id: languageList
                //: English language combo box option
                ListElement { text: QT_TR_NOOP("English"); code: "en" }
                //: German language combo box option
                ListElement { text: QT_TR_NOOP("German"); code: "de" }
                //: French language combo box option
    //            ListElement { text: QT_TR_NOOP("French"); code: "fr" }
                //: Spanish language combo box option
                ListElement { text: QT_TR_NOOP("Spanish"); code: "es" }
                //: Italian language combo box option
    //             ListElement { text: QT_TR_NOOP("Italian"); code: "it" }
                //: Finnish language combo box option
                ListElement { text: QT_TR_NOOP("Finnish"); code: "fi" }
                //: Russian language combo box option
                ListElement { text: QT_TR_NOOP("Russian"); code: "ru" }
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

            Component.onCompleted:
            {
                // Because ListModel is stupid and does not allow using qsTr() for values.
                for(var i = 0; i < languageList.count; ++i)
                {
                    languageList.setProperty(i, "text", catalog.i18nc("@action:menu",languageList.get(i).text));
                }
            }
        }

        Label
        {
            id: languageCaption;
            Layout.fillHeight: true
            Layout.fillWidth: true //only two lines left of qt layouts (nescesseray because PreferencesDialog work with layouts)

            //: Language change warning
            text: catalog.i18nc("@label","You will need to restart the application for language changes to have effect.")
            wrapMode: Text.WordWrap
            font.italic: true
        }
    }
}
