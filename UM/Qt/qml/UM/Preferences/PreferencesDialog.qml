import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import ".."

Window {
    title: "Preferences"
    flags: Qt.Dialog

    width: 640;
    height: 480;

    RowLayout {
        anchors.fill: parent;

        Column {
            Layout.fillHeight: true;

            Repeater {
                model: configPagesModel;
                delegate: Button {
                    width: 100
                    height: 100
                    text: model.name;
                    onClicked: configPage.source = model.page;
                }
            }
        }

        Loader {
            id: configPage;
            Layout.fillWidth: true
            Layout.fillHeight: true

            source: configPagesModel.get(0).page;
        }
    }

    ListModel {
        id: configPagesModel;

        ListElement { name: "General"; page: "GeneralPage.qml"; }
        ListElement { name: "Machine Settings"; page: "../Settings/SettingsConfigurationPage.qml"; }
        ListElement { name: "Plugins"; page: "PluginsPage.qml"; }
    }

    function setPage(index) {
        configPage.source = configPagesModel.get(index).page;
    }
}
