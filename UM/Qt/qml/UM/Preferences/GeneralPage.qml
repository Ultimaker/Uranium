import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

PreferencesPage {
    //: General configuration page title
    title: qsTr("General");

    function reset() {
        UM.Preferences.resetPreference('general/language')
    }

    GridLayout {
        columns: 2;

        //: Language selection label
        Label { text: qsTr("Language"); }
        ComboBox {
            model: ListModel {
                //: English language combo box option
                ListElement { text: QT_TR_NOOP("English"); code: "en" }
                //: German language combo box option
                ListElement { text: QT_TR_NOOP("German"); code: "de" }
                //: French language combo box option
                ListElement { text: QT_TR_NOOP("French"); code: "fr" }
                //: Spanish language combo box option
                ListElement { text: QT_TR_NOOP("Spanish"); code: "es" }
            }

            currentIndex: {
                var code = UM.Preferences.getValue('general/language')
                for(i in model.count) {
                    if(model.get(i).code == code) {
                        return i;
                    }
                }
            }
            onCurrentIndexChanged: UM.Preferences.setValue('general/language', model.get(currentIndex).code)
        }

        Label {
            Layout.columnSpan: 2;
            //: Language change warning
            text: qsTr("You will need to restart the application for language changes to have effect.")

            font.italic: true;
        }

        Item { Layout.fillHeight: true; Layout.columnSpan: 2 }
    }
}
