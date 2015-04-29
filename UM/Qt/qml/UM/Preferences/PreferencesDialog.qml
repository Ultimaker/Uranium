import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import ".."

import UM 1.0 as UM

Dialog {
    id: base;

    //: Preferences dialog title
    title: qsTr("Preferences")

    RowLayout {
        anchors.fill: parent;

        TableView {
            id: pagesList;

            Layout.fillHeight: true;
            Layout.preferredWidth: Screen.pixelDensity * 30;

            alternatingRowColors: false;
            headerVisible: false;

            model: ListModel {
                id: configPagesModel;

                //: General configuration page title
                ListElement { name: QT_TR_NOOP("General"); page: "GeneralPage.qml"; }
                //: Machine configuration page title
                ListElement { name: QT_TR_NOOP("Machine"); page: "../Settings/SettingsConfigurationPage.qml"; }
                //: Plugins configuration page title
                ListElement { name: QT_TR_NOOP("Plugins"); page: "PluginsPage.qml"; }
            }

            TableViewColumn { role: "name" }

            onActivated: configPage.source = configPagesModel.get(row).page;

            Component.onCompleted: pagesList.selection.select(0);
        }

        Loader {
            id: configPage;
            Layout.fillWidth: true
            Layout.fillHeight: true

            source: configPagesModel.get(0).page;
        }
    }

    leftButtons: Button {
        //: Reset preferences to default
        text: qsTr("Defaults");

        onClicked: configPage.item.reset();
    }

    rightButtons: Button {
        //: Close preferences dialog
        text: qsTr("Close");

        onClicked: base.visible = false;
    }

    function setPage(index) {
        configPage.source = configPagesModel.get(index).page;
        pagesList.selection.clear();
        pagesList.selection.select(index);
    }

    function insertPage(index, name, icon, page) {
        configPagesModel.insert(index, { 'name': name, 'icon': icon, 'page': page });
    }
}
