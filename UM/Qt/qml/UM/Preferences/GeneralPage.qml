// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

PreferencesPage {
    //: General configuration page title
    title: qsTr("General");

    function reset() {
        UM.Preferences.resetPreference("general/language")
    }

    //: Language selection label
    Label {
        id: languageLabel
        text: qsTr("Language")
    }

    ComboBox {
        id: languageComboBox
        model: ListModel {
            //: English language combo box option
            ListElement { text: QT_TR_NOOP("English"); code: "en" }
            //: German language combo box option
            ListElement { text: QT_TR_NOOP("German"); code: "de" }
            //: French language combo box option
            ListElement { text: QT_TR_NOOP("French"); code: "fr" }
            //: Spanish language combo box option
            ListElement { text: QT_TR_NOOP("Spanish"); code: "es" }
            //: Italian language combo box option
            ListElement { text: QT_TR_NOOP("Italian"); code: "it" }
            //: Finnish language combo box option
            ListElement { text: QT_TR_NOOP("Finnish"); code: "fi" }
            //: Russian language combo box option
            ListElement { text: QT_TR_NOOP("Russian"); code: "ru" }
        }

        currentIndex: {
            var code = UM.Preferences.getValue("general/language")
            for(i in model.count) {
                if(model.get(i).code == code) {
                    return i
                }
            }
        }
        onCurrentIndexChanged: UM.Preferences.setValue("general/language", model.get(currentIndex).code)

        anchors.left: languageLabel.right
        anchors.top: languageLabel.top
        anchors.leftMargin: 20
    }

    Label {
        id: languageCaption;
        Layout.fillHeight: true
        Layout.fillWidth: true //only two lines left of qt layouts (nescesseray because PreferencesDialog work with layouts)

        //: Language change warning
        text: qsTr("You will need to restart the application for language changes to have effect.")
        wrapMode: Text.WordWrap
        font.italic: true
    }
}
