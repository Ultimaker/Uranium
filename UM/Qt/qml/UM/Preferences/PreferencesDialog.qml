import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import ".."

Window {
    //: Preferences dialog title
    title: qsTr("Preferences")
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

        //: General configuration page title
        ListElement { name: QT_TR_NOOP("General"); page: "GeneralPage.qml"; }
        //: Machine configuration page title
        ListElement { name: QT_TR_NOOP("Machine"); page: "../Settings/SettingsConfigurationPage.qml"; }
        //: Plugins configuration page title
        ListElement { name: QT_TR_NOOP("Plugins"); page: "PluginsPage.qml"; }
    }

    function setPage(index) {
        configPage.source = configPagesModel.get(index).page;
    }
}
