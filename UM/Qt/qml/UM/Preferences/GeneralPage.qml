import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

PreferencesPage {
    //: General configuration page title
    title: qsTr("General");

    GridLayout {
        columns: 2;

        //: Language selection label
        Label { text: qsTr("Language"); }
        ComboBox { model: ['English', 'x-test'] }

        Label {
            Layout.columnSpan: 2;
            //: Language change warning
            text: qsTr("You will need to restart the application for language changes to have effect.")

            font.italic: true;
        }

        Item { Layout.fillHeight: true; Layout.columnSpan: 2 }
    }
}
